from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.schemas.document import DocumentSummary


@dataclass(frozen=True)
class DocumentRecord:
    id: str
    title: str
    owner_id: str
    storage_bucket: str
    storage_path: str
    head_revision: int
    updated_at: datetime


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_user(self, user_id: str) -> list[DocumentSummary]:
        rows = self._session.execute(
            text(
                """
                select
                  d.id::text as id,
                  d.title,
                  d.owner_id::text as owner_id,
                  d.head_revision,
                  d.updated_at
                from public.documents d
                where d.deleted_at is null
                  and (
                    d.owner_id = cast(:user_id as uuid)
                    or exists (
                      select 1
                      from public.document_members dm
                      where dm.document_id = d.id
                        and dm.user_id = cast(:user_id as uuid)
                        and dm.role in ('owner', 'editor')
                    )
                  )
                order by d.updated_at desc
                """
            ),
            {"user_id": user_id},
        ).mappings()

        return [self._summary_from_row(row) for row in rows]

    def get_accessible(self, document_id: str, user_id: str) -> DocumentRecord | None:
        row = self._session.execute(
            text(
                """
                select
                  d.id::text as id,
                  d.title,
                  d.owner_id::text as owner_id,
                  d.storage_bucket,
                  d.storage_path,
                  d.head_revision,
                  d.updated_at
                from public.documents d
                where d.id = cast(:document_id as uuid)
                  and d.deleted_at is null
                  and (
                    d.owner_id = cast(:user_id as uuid)
                    or exists (
                      select 1
                      from public.document_members dm
                      where dm.document_id = d.id
                        and dm.user_id = cast(:user_id as uuid)
                        and dm.role in ('owner', 'editor')
                    )
                  )
                """
            ),
            {"document_id": document_id, "user_id": user_id},
        ).mappings().one_or_none()

        if row is None:
            return None

        return self._record_from_row(row)

    def create(
        self,
        document_id: str,
        owner_id: str,
        title: str,
        storage_path: str,
    ) -> DocumentRecord:
        row = self._session.execute(
            text(
                """
                insert into public.documents (id, owner_id, title, storage_path)
                values (
                  cast(:document_id as uuid),
                  cast(:owner_id as uuid),
                  :title,
                  :storage_path
                )
                returning
                  id::text as id,
                  title,
                  owner_id::text as owner_id,
                  storage_bucket,
                  storage_path,
                  head_revision,
                  updated_at
                """
            ),
            {
                "document_id": document_id,
                "owner_id": owner_id,
                "title": title,
                "storage_path": storage_path,
            },
        ).mappings().one()

        self._session.execute(
            text(
                """
                insert into public.document_members (document_id, user_id, role)
                values (
                  cast(:document_id as uuid),
                  cast(:owner_id as uuid),
                  'owner'
                )
                on conflict (document_id, user_id) do update
                set role = excluded.role
                """
            ),
            {"document_id": document_id, "owner_id": owner_id},
        )

        return self._record_from_row(row)

    def update_editable(
        self,
        document_id: str,
        user_id: str,
        title: str | None,
        content_changed: bool,
    ) -> DocumentRecord | None:
        row = self._session.execute(
            text(
                """
                update public.documents
                set
                  title = coalesce(:title, title),
                  head_revision = case
                    when :content_changed then head_revision + 1
                    else head_revision
                  end,
                  snapshot_version = case
                    when :content_changed then snapshot_version + 1
                    else snapshot_version
                  end
                where id = cast(:document_id as uuid)
                  and deleted_at is null
                  and (
                    owner_id = cast(:user_id as uuid)
                    or exists (
                      select 1
                      from public.document_members dm
                      where dm.document_id = public.documents.id
                        and dm.user_id = cast(:user_id as uuid)
                        and dm.role in ('owner', 'editor')
                    )
                  )
                returning
                  id::text as id,
                  title,
                  owner_id::text as owner_id,
                  storage_bucket,
                  storage_path,
                  head_revision,
                  updated_at
                """
            ),
            {
                "document_id": document_id,
                "user_id": user_id,
                "title": title,
                "content_changed": content_changed,
            },
        ).mappings().one_or_none()

        if row is None:
            return None

        return self._record_from_row(row)

    def soft_delete_owned(self, document_id: str, owner_id: str) -> bool:
        row = self._session.execute(
            text(
                """
                update public.documents
                set deleted_at = now()
                where id = cast(:document_id as uuid)
                  and owner_id = cast(:owner_id as uuid)
                  and deleted_at is null
                returning id
                """
            ),
            {"document_id": document_id, "owner_id": owner_id},
        ).one_or_none()

        return row is not None

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def _summary_from_row(self, row: RowMapping) -> DocumentSummary:
        return DocumentSummary(
            id=str(row["id"]),
            title=str(row["title"]),
            owner_id=str(row["owner_id"]),
            head_revision=int(cast(int, row["head_revision"])),
            updated_at=cast(datetime, row["updated_at"]),
        )

    def _record_from_row(self, row: RowMapping) -> DocumentRecord:
        return DocumentRecord(
            id=str(row["id"]),
            title=str(row["title"]),
            owner_id=str(row["owner_id"]),
            storage_bucket=str(row["storage_bucket"]),
            storage_path=str(row["storage_path"]),
            head_revision=int(cast(int, row["head_revision"])),
            updated_at=cast(datetime, row["updated_at"]),
        )


def get_document_repository(
    session: Annotated[Session, Depends(get_db_session)],
) -> DocumentRepository:
    return DocumentRepository(session=session)
