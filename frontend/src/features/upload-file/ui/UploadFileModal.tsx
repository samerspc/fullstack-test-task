"use client";

import { FormEvent, useState } from "react";
import { Button, Form, Modal } from "react-bootstrap";

import { filesApi } from "@/shared/api/files";

type Props = {
  show: boolean;
  onHide: () => void;
  onUploaded: () => void | Promise<void>;
};

export function UploadFileModal({ show, onHide, onUploaded }: Props) {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function reset() {
    setTitle("");
    setFile(null);
    setError(null);
    setIsSubmitting(false);
  }

  function handleHide() {
    reset();
    onHide();
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!title.trim() || !file) {
      setError("Укажите название и выберите файл");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await filesApi.create(title.trim(), file);
      await onUploaded();
      reset();
      onHide();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось загрузить файл");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal show={show} onHide={handleHide} centered>
      <Form onSubmit={handleSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>Добавить файл</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error ? <div className="alert alert-danger py-2 px-3">{error}</div> : null}
          <Form.Group className="mb-3">
            <Form.Label>Название</Form.Label>
            <Form.Control
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Например, Договор с подрядчиком"
              maxLength={255}
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>Файл</Form.Label>
            <Form.Control
              type="file"
              onChange={(event) =>
                setFile((event.target as HTMLInputElement).files?.[0] ?? null)
              }
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={handleHide}>
            Отмена
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? "Загрузка..." : "Сохранить"}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
