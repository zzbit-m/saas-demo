import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../auth";
import {
  createNote,
  deleteNote,
  getOrg,
  inviteMember,
  listMembers,
  listNotes,
  removeMember,
  updateNote,
} from "../api";

interface Org {
  id: string;
  name: string;
  slug: string;
}

interface Member {
  user_id: string;
  email: string;
  role: string;
}

interface Note {
  id: string;
  title: string;
  body: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export default function OrgPage() {
  const { user } = useAuth();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [org, setOrg] = useState<Org | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);

  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("member");
  const [inviteError, setInviteError] = useState("");

  const [noteTitle, setNoteTitle] = useState("");
  const [noteBody, setNoteBody] = useState("");
  const [noteError, setNoteError] = useState("");

  const [editingNote, setEditingNote] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editBody, setEditBody] = useState("");

  const userRole = members.find((m) => m.user_id === user?.id)?.role;
  const isAdmin = userRole === "owner" || userRole === "admin";

  const fetchData = useCallback(async () => {
    if (!id) return;
    try {
      const [orgData, membersData, notesData] = await Promise.all([
        getOrg(id),
        listMembers(id),
        listNotes(id),
      ]);
      setOrg(orgData);
      setMembers(membersData);
      setNotes(notesData);
    } catch {
      navigate("/");
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setInviteError("");
    try {
      const m = await inviteMember(id, inviteEmail, inviteRole);
      setMembers((prev) => [...prev, m]);
      setInviteEmail("");
    } catch (err: unknown) {
      setInviteError(
        err instanceof Error ? err.message : "Failed to invite",
      );
    }
  }

  async function handleRemoveMember(userId: string) {
    if (!id) return;
    try {
      await removeMember(id, userId);
      setMembers((prev) => prev.filter((m) => m.user_id !== userId));
    } catch {
      // ignore
    }
  }

  async function handleCreateNote(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    setNoteError("");
    try {
      const n = await createNote(id, noteTitle, noteBody);
      setNotes((prev) => [...prev, n]);
      setNoteTitle("");
      setNoteBody("");
    } catch (err: unknown) {
      setNoteError(
        err instanceof Error ? err.message : "Failed to create note",
      );
    }
  }

  async function handleUpdateNote(noteId: string) {
    if (!id) return;
    try {
      const updated = await updateNote(id, noteId, editTitle, editBody);
      setNotes((prev) =>
        prev.map((n) => (n.id === noteId ? { ...n, ...updated } : n)),
      );
      setEditingNote(null);
    } catch {
      // ignore
    }
  }

  async function handleDeleteNote(noteId: string) {
    if (!id) return;
    try {
      await deleteNote(id, noteId);
      setNotes((prev) => prev.filter((n) => n.id !== noteId));
    } catch {
      // ignore
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (!org) return null;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-6">
        <Link
          to="/"
          className="text-sm text-blue-600 hover:underline"
        >
          &larr; Back to orgs
        </Link>
        <h1 className="mt-1 text-2xl font-bold">{org.name}</h1>
        <p className="text-sm text-gray-500">{org.slug}</p>
      </div>

      <div className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">
          Members ({members.length})
        </h2>
        <div className="space-y-2">
          {members.map((m) => (
            <div
              key={m.user_id}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-4 py-2"
            >
              <div>
                <span className="font-medium">{m.email}</span>
                <span className="ml-2 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  {m.role}
                </span>
              </div>
              {isAdmin && m.user_id !== user?.id && (
                <button
                  onClick={() => handleRemoveMember(m.user_id)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>

        {isAdmin && (
          <form onSubmit={handleInvite} className="mt-3 flex gap-2">
            <input
              type="email"
              placeholder="Email"
              required
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              className="block flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            >
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
            >
              Invite
            </button>
          </form>
        )}
        {inviteError && (
          <p className="mt-2 text-sm text-red-600">{inviteError}</p>
        )}
      </div>

      <div>
        <h2 className="mb-3 text-lg font-semibold">
          Notes ({notes.length})
        </h2>

        <form
          onSubmit={handleCreateNote}
          className="mb-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
        >
          <input
            type="text"
            placeholder="Title"
            required
            value={noteTitle}
            onChange={(e) => setNoteTitle(e.target.value)}
            className="mb-2 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <textarea
            placeholder="Body (optional)"
            rows={3}
            value={noteBody}
            onChange={(e) => setNoteBody(e.target.value)}
            className="mb-2 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          {noteError && (
            <p className="mb-2 text-sm text-red-600">{noteError}</p>
          )}
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            Add note
          </button>
        </form>

        <div className="space-y-3">
          {notes.length === 0 && (
            <p className="py-8 text-center text-gray-500">
              No notes yet. Create the first one.
            </p>
          )}
          {notes.map((note) => {
            const isAuthor = note.created_by === user?.id;
            const canEdit = isAuthor || isAdmin;

            return (
              <div
                key={note.id}
                className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
              >
                {editingNote === note.id ? (
                  <div>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="mb-2 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                    />
                    <textarea
                      rows={3}
                      value={editBody}
                      onChange={(e) => setEditBody(e.target.value)}
                      className="mb-2 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleUpdateNote(note.id)}
                        className="rounded-lg bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingNote(null)}
                        className="rounded-lg border border-gray-300 px-3 py-1 text-sm hover:bg-gray-100"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold">{note.title}</h3>
                        {note.body && (
                          <p className="mt-1 text-sm text-gray-600 whitespace-pre-wrap">
                            {note.body}
                          </p>
                        )}
                      </div>
                      {canEdit && (
                        <div className="flex gap-1">
                          <button
                            onClick={() => {
                              setEditingNote(note.id);
                              setEditTitle(note.title);
                              setEditBody(note.body);
                            }}
                            className="rounded px-2 py-1 text-xs text-gray-600 hover:bg-gray-100"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteNote(note.id)}
                            className="rounded px-2 py-1 text-xs text-red-600 hover:bg-red-50"
                          >
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                    <p className="mt-2 text-xs text-gray-400">
                      by{" "}
                      {members.find((m) => m.user_id === note.created_by)
                        ?.email ?? note.created_by}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
