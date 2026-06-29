import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useEffect } from "react";

type TipTapDocumentEditorProps = {
  content: string;
  onChange: (content: string) => void;
};

const escapeHtml = (value: string) =>
  value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const textToHtml = (content: string) => {
  if (!content) {
    return "<p></p>";
  }

  return content
    .split("\n")
    .map((line) => `<p>${line ? escapeHtml(line) : "<br>"}</p>`)
    .join("");
};

export function TipTapDocumentEditor({
  content,
  onChange,
}: TipTapDocumentEditorProps) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: textToHtml(content),
    editorProps: {
      attributes: {
        class:
          "min-h-[360px] rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 text-sm leading-6 outline-none",
      },
    },
    onUpdate: ({ editor: currentEditor }) => {
      onChange(currentEditor.getText());
    },
  });

  useEffect(() => {
    if (!editor) {
      return;
    }

    if (editor.getText() !== content) {
      editor.commands.setContent(textToHtml(content), { emitUpdate: false });
    }
  }, [content, editor]);

  return <EditorContent editor={editor} />;
}
