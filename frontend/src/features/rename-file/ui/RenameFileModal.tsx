"use client";

import { FormEvent, useEffect, useState } from "react";
import { Button, Form, Modal } from "react-bootstrap";

import type { FileItem } from "@/entities/file/model/types";
import { filesApi } from "@/shared/api/files";

type Props = {
  file: FileItem | null;
  onHide: () => void;
  onUpdated: () => void | Promise<void>;
};

export function RenameFileModal({ file, onHide, onUpdated }: Props) {
  const [title, setTitle] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setTitle(file?.title ?? "");
    setError(null);
  }, [file]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;

    if (!title.trim()) {
      setError("Введите новое название");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await filesApi.rename(file.id, title.trim());
      await onUpdated();
      onHide();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось сохранить изменения");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal show={file !== null} onHide={onHide} centered>
      <Form onSubmit={handleSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>Переименовать</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error ? <div className="alert alert-danger py-2 px-3">{error}</div> : null}
          <Form.Group>
            <Form.Label>Название</Form.Label>
            <Form.Control
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              maxLength={255}
              autoFocus
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>
            Отмена
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? "Сохранение..." : "Сохранить"}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
