"use client";

import { useState } from "react";
import { Alert, Badge, Button, Card, Col, Container, Row } from "react-bootstrap";

import { AlertsTable } from "@/features/alerts-list/ui/AlertsTable";
import { DeleteFileDialog } from "@/features/delete-file/ui/DeleteFileDialog";
import { FilesTable } from "@/features/files-list/ui/FilesTable";
import { RenameFileModal } from "@/features/rename-file/ui/RenameFileModal";
import { UploadFileModal } from "@/features/upload-file/ui/UploadFileModal";
import { useAlerts } from "@/features/alerts-list/model/useAlerts";
import { useFiles } from "@/features/files-list/model/useFiles";
import type { FileItem } from "@/entities/file/model/types";

export function FilesPage() {
  const { files, isLoading: filesLoading, error: filesError, refetch: refetchFiles } = useFiles();
  const {
    alerts,
    isLoading: alertsLoading,
    error: alertsError,
    refetch: refetchAlerts,
  } = useAlerts();

  const [uploadOpen, setUploadOpen] = useState(false);
  const [fileToRename, setFileToRename] = useState<FileItem | null>(null);
  const [fileToDelete, setFileToDelete] = useState<FileItem | null>(null);

  async function refetchAll() {
    await Promise.all([refetchFiles(), refetchAlerts()]);
  }

  const error = filesError ?? alertsError;

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <Card className="shadow-sm border-0 mb-4">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                <div>
                  <h1 className="h3 mb-2">Управление файлами</h1>
                  <p className="text-secondary mb-0">
                    Загрузка файлов, просмотр статусов обработки и ленты алертов.
                  </p>
                </div>
                <div className="d-flex gap-2">
                  <Button variant="outline-secondary" onClick={() => void refetchAll()}>
                    Обновить
                  </Button>
                  <Button variant="primary" onClick={() => setUploadOpen(true)}>
                    Добавить файл
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {error ? (
            <Alert variant="danger" className="shadow-sm">
              {error}
            </Alert>
          ) : null}

          <Card className="shadow-sm border-0 mb-4">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Файлы</h2>
                <Badge bg="secondary">{files.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <FilesTable
                files={files}
                isLoading={filesLoading}
                onRename={setFileToRename}
                onDelete={setFileToDelete}
              />
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Алерты</h2>
                <Badge bg="secondary">{alerts.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <AlertsTable alerts={alerts} isLoading={alertsLoading} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <UploadFileModal
        show={uploadOpen}
        onHide={() => setUploadOpen(false)}
        onUploaded={refetchAll}
      />
      <RenameFileModal
        file={fileToRename}
        onHide={() => setFileToRename(null)}
        onUpdated={refetchAll}
      />
      <DeleteFileDialog
        file={fileToDelete}
        onHide={() => setFileToDelete(null)}
        onDeleted={refetchAll}
      />
    </Container>
  );
}
