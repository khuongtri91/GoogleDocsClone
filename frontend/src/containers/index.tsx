import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { LoadingContainer, MainLayout } from "../components";
import { PATHS } from "../utils/path";

const AuthManagement = lazy(() => import("./AuthManagement"));

export function AppContainers() {
  return (
    <MainLayout>
      <Suspense fallback={<LoadingContainer />}>
        <Routes>
          <Route path={PATHS.home} element={<AuthManagement />} />
          <Route path={PATHS.authCallback} element={<AuthManagement />} />
        </Routes>
      </Suspense>
    </MainLayout>
  );
}
