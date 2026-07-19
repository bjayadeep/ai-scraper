"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  Briefcase, 
  Search, 
  MapPin, 
  Calendar, 
  ExternalLink,
  RefreshCw,
  Award
} from "lucide-react";
import api from "@/lib/api";

export default function JobsPage() {
  const [search, setSearch] = useState("");
  const [companyFilter, setCompanyFilter] = useState("");
  const [page, setPage] = useState(1);

  // Fetch Jobs Board Query
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["jobs", search, companyFilter, page],
    queryFn: async () => {
      const response = await api.get("/jobs", {
        params: { 
          page, 
          search: search || undefined, 
          company: companyFilter || undefined, 
          limit: 12 
        },
      });
      return response.data;
    },
  });

  const totalPages = data ? Math.ceil(data.total / data.limit) : 1;

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "n/a";
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    });
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-[#1E293B]">Aggregated Job Leads</h1>
          <p className="text-xs text-[#5B5F4A]">
            US-based Cyber Security roles matching 1–6 years of experience
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="btn-secondary flex items-center gap-1.5 text-xs py-1.5 px-3 font-semibold rounded-xl"
        >
          <RefreshCw className={`h-3 w-3 ${isFetching ? "animate-spin" : ""}`} />
          <span>Refresh leads</span>
        </button>
      </div>

      {/* Filter toolbar */}
      <div className="flex flex-col gap-4 sm:flex-row items-center justify-between border border-[#EADFCF] bg-[#FFFDFC] p-4 rounded-xl shadow-xs">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="absolute top-1/2 left-3 h-3.5 w-3.5 -translate-y-1/2 text-[#5B5F4A]/70" />
          <input
            type="text"
            placeholder="Search job title, company, location..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full rounded-xl border border-[#EADFCF] bg-[#FFFDFC] px-8 py-1.5 text-xs text-[#1E293B] placeholder-gray-400 transition focus:border-[#2F6F5E] focus:ring-2 focus:ring-[#2F6F5E]/10 outline-none"
          />
        </div>

        {/* Company Filter */}
        <input
          type="text"
          placeholder="Filter by company name..."
          value={companyFilter}
          onChange={(e) => { setCompanyFilter(e.target.value); setPage(1); }}
          className="w-full sm:w-60 rounded-xl border border-[#EADFCF] bg-[#FFFDFC] px-3 py-1.5 text-xs text-[#1E293B] placeholder-gray-400 transition focus:border-[#2F6F5E] focus:ring-2 focus:ring-[#2F6F5E]/10 outline-none"
        />
      </div>

      {/* Leads Content Board */}
      <div className="border border-[#EADFCF] bg-[#FFFDFC] p-6 rounded-xl shadow-xs">
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-40 rounded-xl bg-[#FFF9F0] border border-[#EADFCF]"></div>
            ))}
          </div>
        ) : data?.data?.length > 0 ? (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {data.data.map((job: any) => (
                <div key={job.id} className="flex flex-col justify-between rounded-xl border border-[#EADFCF] bg-[#FFFDFC] p-4.5 hover:border-[#D1C4B2] hover:shadow-sm transition duration-150">
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <span className="badge badge-gray text-[9px] font-bold uppercase tracking-wide px-2 py-0.5 border border-[#EADFCF] bg-[#FFF9F0] text-[#5B5F4A]">
                        {job.company}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-[#1E293B] leading-snug line-clamp-2">
                      {job.title}
                    </h3>

                    {/* Metadata lines */}
                    <div className="space-y-1.5 pt-0.5 text-[10px] text-[#5B5F4A] font-semibold">
                      <div className="flex items-center gap-1.5">
                        <MapPin className="h-3 w-3 text-[#5B5F4A]/60 shrink-0" />
                        <span className="truncate">{job.location || "USA / Remote"}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Award className="h-3 w-3 text-[#5B5F4A]/60 shrink-0" />
                        <span className="truncate">{job.experience_metadata || "Experience details not specified"}</span>
                      </div>
                    </div>
                  </div>

                  {/* Footer link details */}
                  <div className="mt-4 pt-3.5 border-t border-[#FFF9F0] flex items-center justify-between text-[10px] font-bold text-[#5B5F4A]">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3 text-[#5B5F4A]/50" />
                      <span>{formatDate(job.date_posted)}</span>
                    </span>
                    <a
                      href={job.apply_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[#C67C2E] hover:text-[#A9621C] transition"
                    >
                      <span>Apply</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="mt-6 flex items-center justify-between border-t border-[#EADFCF] pt-5">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-secondary py-1 px-3 text-[10px] font-semibold rounded-xl"
                >
                  Previous
                </button>
                <span className="text-[10px] font-bold text-[#5B5F4A]">
                  Page {page} of {totalPages} (Total leads: {data.total})
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="btn-secondary py-1 px-3 text-[10px] font-semibold rounded-xl"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-[#5B5F4A]">
            <Briefcase className="h-10 w-10 text-[#EADFCF] mb-2" />
            <h3 className="text-sm font-bold text-[#1E293B]">No job leads identified</h3>
            <p className="text-[11px] mt-0.5">Try altering the search filters or trigger manual scrapes.</p>
          </div>
        )}
      </div>
    </div>
  );
}
