"use client";

import { Badge, Button, Spinner, Table } from "react-bootstrap";

import { ProcessingBadge } from "@/entities/file/ui/ProcessingBadge";
import { ScanBadge } from "@/entities/file/ui/ScanBadge";
import type { FileItem } from "@/entities/file/model/types";
import { formatDate, formatSize } from "@/shared/lib/format";
import { filesApi } from "@/shared/api/files";

type Props = {
  files: FileItem[];
  isLoading: boolean;
  onRename: (file: FileItem) => void;
  onDelete: (file: FileItem) => void;
};

export function FilesTable({ files, isLoading, onRename, onDelete }: Props) {
  if (isLoading) {
    return (
      <div className="d-flex justify-content-center py-5">
        <Spinner animation="border" />
      </div>
    );
  }

  return (
    <div className="table-responsive">
      <Table hover bordered className="align-middle mb-0">
        <thead className="table-light">
          <tr>
            <th>Название</th>
            <th>Файл</th>
            <th>MIME</th>
            <th>Размер</th>
            <th>Статус</th>
            <th>Проверка</th>
            <th>Создан</th>
            <th className="text-end">Действия</th>
          </tr>
        </thead>
        <tbody>
          {files.length === 0 ? (
            <tr>
              <td colSpan={8} className="text-center py-4 text-secondary">
                Файлы пока не загружены
              </td>
            </tr>
          ) : (
            files.map((file) => (
              <tr key={file.id}>
                <td>
                  <div className="fw-semibold">{file.title}</div>
                  <div className="small text-secondary">{file.id}</div>
                </td>
                <td>{file.original_name}</td>
                <td>
                  <Badge bg="light" text="dark" className="border">
                    {file.mime_type}
                  </Badge>
                </td>
                <td>{formatSize(file.size)}</td>
                <td>
                  <ProcessingBadge status={file.processing_status} />
                </td>
                <td>
                  <ScanBadge
                    status={file.scan_status}
                    requiresAttention={file.requires_attention}
                    details={file.scan_details}
                  />
                </td>
                <td>{formatDate(file.created_at)}</td>
                <td className="text-nowrap text-end">
                  <div className="d-inline-flex gap-1">
                    <Button
                      as="a"
                      href={filesApi.downloadUrl(file.id)}
                      variant="outline-primary"
                      size="sm"
                    >
                      Скачать
                    </Button>
                    <Button variant="outline-secondary" size="sm" onClick={() => onRename(file)}>
                      Переименовать
                    </Button>
                    <Button variant="outline-danger" size="sm" onClick={() => onDelete(file)}>
                      Удалить
                    </Button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    </div>
  );
}
