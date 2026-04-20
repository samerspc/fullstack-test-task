"use client";

import { useState } from "react";
import { Button, Modal } from "react-bootstrap";

import type { FileItem } from "@/entities/file/model/types";
import { filesApi } from "@/shared/api/files";

type Props = {
  file: FileItem | null;
  onHide: () => void;
  onDeleted: () => void | Promise<void>;
};

export function DeleteFileDialog({ file, onHide, onDeleted }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleConfirm() {
    if (!file) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await filesApi.remove(file.id);
      await onDeleted();
      onHide();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось удалить файл");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal show={file !== null} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Удалить файл?</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error ? <div className="alert alert-danger py-2 px-3">{error}</div> : null}
        <p className="mb-0">
          Файл <strong>{file?.title}</strong> и связанные алерты будут удалены без возможности
          восстановления.
        </p>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onHide} disabled={isSubmitting}>
          Отмена
        </Button>
        <Button variant="danger" onClick={handleConfirm} disabled={isSubmitting}>
          {isSubmitting ? "Удаление..." : "Удалить"}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}
