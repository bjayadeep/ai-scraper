"use client";

import React, { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { 
  Users, 
  Plus, 
  Trash2, 
  X, 
  AlertCircle, 
  ShieldCheck,
  UserCheck
} from "lucide-react";
import api from "@/lib/api";

export default function UsersPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isAdmin, setIsAdmin] = useState(false);
  const [loadingRole, setLoadingRole] = useState(true);

  // Modal states
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [currentSelectedUser, setCurrentSelectedUser] = useState<any>(null);

  // Form fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("editor");
  const [formError, setFormError] = useState("");

  // Role validation
  useEffect(() => {
    const userRole = localStorage.getItem("role");
    if (userRole !== "admin") {
      router.push("/dashboard");
    } else {
      setIsAdmin(true);
    }
    setLoadingRole(false);
  }, [router]);

  // Fetch Users Query
  const { data: users, isLoading } = useQuery({
    queryKey: ["users"],
    queryFn: async () => {
      const response = await api.get("/users");
      return response.data;
    },
    enabled: isAdmin,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: async (newUser: any) => {
      const response = await api.post("/users", newUser);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      closeAddModal();
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || "Failed to create user account.");
    }
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await api.delete(`/users/${id}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setIsDeleteOpen(false);
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || "Failed to delete user account.");
    }
  });

  const openAddModal = () => {
    setEmail("");
    setPassword("");
    setRole("editor");
    setFormError("");
    setIsAddOpen(true);
  };

  const closeAddModal = () => {
    setIsAddOpen(false);
  };

  const openDeleteModal = (user: any) => {
    setCurrentSelectedUser(user);
    setIsDeleteOpen(true);
  };

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");

    if (!email || !password || !role) {
      setFormError("All fields are required.");
      return;
    }

    createMutation.mutate({ email, password, role });
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    });
  };

  if (loadingRole || isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="flex justify-between items-center">
          <div className="space-y-1.5">
            <div className="h-6 w-36 rounded-xl bg-[#EADFCF]"></div>
            <div className="h-3 w-52 rounded-xl bg-[#EADFCF]"></div>
          </div>
          <div className="h-8 w-24 rounded-xl bg-[#EADFCF]"></div>
        </div>
        <div className="h-80 rounded-xl bg-[#EADFCF] border border-[#EADFCF]"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-[#1E293B]">Console Operators</h1>
          <p className="text-xs text-[#5B5F4A]">
            Create and manage access settings for recruitment scraper operators
          </p>
        </div>
        <button
          onClick={openAddModal}
          className="btn-primary inline-flex items-center gap-1.5 text-xs py-2 px-4 font-semibold bg-[#C67C2E] text-white hover:bg-[#A9621C] rounded-xl"
        >
          <Plus className="h-4 w-4" />
          <span>Create Operator</span>
        </button>
      </div>

      {/* Users Table Card */}
      <div className="border border-[#EADFCF] bg-[#FFFDFC] rounded-xl shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs text-[#1E293B]">
            <thead className="bg-[#FFF9F0] border-b border-[#EADFCF] text-[10px] font-bold uppercase tracking-wider text-[#5B5F4A]">
              <tr>
                <th className="px-6 py-3.5">User Email</th>
                <th className="px-6 py-3.5">Console Role</th>
                <th className="px-6 py-3.5">Created Date</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#EADFCF]/60">
              {users?.length > 0 ? (
                users.map((user: any) => {
                  const isSelf = localStorage.getItem("email") === user.email;
                  return (
                    <tr key={user.id} className="hover:bg-[#FFF9F0]/60 transition-colors">
                      <td className="px-6 py-3.5 font-bold text-[#1E293B]">
                        <div className="flex items-center gap-2">
                          <span>{user.email}</span>
                          {isSelf && (
                            <span className="inline-flex rounded-full bg-[#FFF9F0] px-2 py-0.5 text-[9px] font-bold text-[#5B5F4A] border border-[#EADFCF]">
                              Current Session
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-3.5">
                        <div className="flex items-center gap-1.5">
                          {user.role === "admin" ? (
                            <ShieldCheck className="h-3.5 w-3.5 text-[#C53030]" />
                          ) : (
                            <UserCheck className="h-3.5 w-3.5 text-blue-600" />
                          )}
                          <span className={`text-xs font-semibold capitalize ${
                            user.role === "admin" ? "text-[#C53030]" : "text-blue-600"
                          }`}>
                            {user.role}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-3.5 text-[#5B5F4A] font-mono text-[10px]">
                        {formatDate(user.created_at)}
                      </td>
                      <td className="px-6 py-3.5 text-right">
                        {!isSelf ? (
                          <button
                            onClick={() => openDeleteModal(user)}
                            title="Delete user operator"
                            className="inline-flex h-7 w-7 items-center justify-center rounded-xl border border-[#EADFCF] bg-[#FFFDFC] text-[#5B5F4A] hover:bg-red-50 hover:text-[#C53030] hover:border-red-200 transition active:scale-95 cursor-pointer"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        ) : (
                          <span className="text-[10px] text-gray-400 italic">Protected</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-10 text-center text-[#5B5F4A]">
                    No operator accounts configured.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* --- ADD USER MODAL --- */}
      {isAddOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-500/20 p-4 backdrop-blur-xs">
          <div className="relative w-full max-w-md rounded-xl border border-[#EADFCF] bg-[#FFF9F0] p-6 shadow-2xl animate-in fade-in duration-150">
            <button onClick={closeAddModal} className="absolute top-4 right-4 text-[#5B5F4A]/70 hover:text-[#1E293B]">
              <X className="h-4 w-4" />
            </button>
            <h3 className="text-sm font-bold uppercase tracking-wider text-[#1E293B] mb-1">Create Operator Account</h3>
            <p className="text-[10px] text-[#5B5F4A] mb-6">Setup new console access credentials</p>
            
            <form onSubmit={handleCreate} className="space-y-4">
              {formError && (
                <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-[#C53030] font-semibold animate-in fade-in">
                  <AlertCircle className="h-4.5 w-4.5 shrink-0 text-[#C53030]" />
                  <span>{formError}</span>
                </div>
              )}

              {/* Email */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-[#5B5F4A]">Email Address</label>
                <input
                  type="email"
                  required
                  placeholder="operator@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-xl border border-[#EADFCF] bg-[#FFFDFC] px-3 py-2 text-xs text-[#1E293B] outline-none focus:border-[#2F6F5E] focus:ring-2 focus:ring-[#2F6F5E]/10 transition"
                />
              </div>

              {/* Password */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-[#5B5F4A]">Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-xl border border-[#EADFCF] bg-[#FFFDFC] px-3 py-2 text-xs text-[#1E293B] outline-none focus:border-[#2F6F5E] focus:ring-2 focus:ring-[#2F6F5E]/10 transition"
                />
              </div>

              {/* Role */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-[#5B5F4A]">Role Privilege</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full rounded-xl border border-[#EADFCF] bg-[#FFFDFC] px-3 py-2 text-xs text-[#1E293B] outline-none focus:border-[#2F6F5E] transition cursor-pointer font-semibold text-[#5B5F4A]"
                >
                  <option value="editor">Editor (Scraper runs & Setting configurations)</option>
                  <option value="admin">Administrator (Full privileges + operator CRUD)</option>
                </select>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2.5 justify-end pt-4 border-t border-[#EADFCF]">
                <button
                  type="button"
                  onClick={closeAddModal}
                  className="btn-secondary py-1.5 px-3 text-[10px] font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="btn-primary py-1.5 px-4 text-[10px] font-semibold bg-[#C67C2E] text-white hover:bg-[#A9621C] rounded-xl"
                >
                  {createMutation.isPending ? "Creating..." : "Create Account"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- DELETE CONFIRM MODAL --- */}
      {isDeleteOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-500/20 p-4 backdrop-blur-xs">
          <div className="w-full max-w-sm rounded-xl border border-[#EADFCF] bg-[#FFF9F0] p-5 shadow-2xl animate-in fade-in duration-150">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[#1E293B] mb-2">Delete Operator Account</h3>
            <p className="text-xs text-[#5B5F4A] mb-5 leading-normal">
              Confirm deleting operator <span className="text-[#1E293B] font-semibold">{currentSelectedUser?.email}</span>? Authentication keys will be deleted immediately.
            </p>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setIsDeleteOpen(false)}
                className="btn-secondary py-1.5 px-3 text-[10px] font-semibold rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={() => deleteMutation.mutate(currentSelectedUser.id)}
                disabled={deleteMutation.isPending}
                className="rounded-xl bg-[#C53030] px-3 py-1.5 text-[10px] font-bold text-white hover:bg-[#A92222] active:scale-95 transition cursor-pointer"
              >
                {deleteMutation.isPending ? "Removing..." : "Delete Account"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
