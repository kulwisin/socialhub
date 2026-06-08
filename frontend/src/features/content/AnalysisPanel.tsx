"use client";

import { useState } from "react";
import {
  Brain,
  Sparkles,
  X,
  Copy,
  ChevronDown,
  ChevronUp,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  useGetAnalysis,
  useListGenerated,
  useAnalyzeFile,
  useGenerateCopy,
} from "@/hooks/useContent";
import type { AiAnalysis, ContentFile, GeneratedContent } from "@/types";
import { toast } from "sonner";

const PLATFORM_EMOJI: Record<string, string> = {
  instagram: "📸",
  tiktok: "🎵",
  youtube: "▶️",
  x: "𝕏",
  threads: "🧵",
  snapchat: "👻",
};

function ScoreBar({ score }: { score: number }) {
  const color =
    score >= 75 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-400";
  return (
    <div className="flex items-center gap-3">
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="w-8 text-right text-sm font-semibold">{score}</span>
    </div>
  );
}

function TagList({ items, color }: { items: string[]; color: string }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <span
          key={item}
          className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${color}`}
        >
          {item}
        </span>
      ))}
    </div>
  );
}

function CopyBlock({ item }: { item: GeneratedContent }) {
  const [open, setOpen] = useState(false);

  const copyText = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  const fullCaption = [
    item.hook,
    item.caption,
    item.cta,
    item.hashtags?.map((h) => `#${h}`).join(" "),
  ]
    .filter(Boolean)
    .join("\n\n");

  return (
    <div className="rounded-xl border border-border bg-card">
      <button
        className="flex w-full items-center justify-between px-4 py-3 text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="flex items-center gap-2 font-medium">
          <span>{PLATFORM_EMOJI[item.platform] ?? "📱"}</span>
          <span className="capitalize">{item.platform}</span>
        </span>
        {open ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>

      {open && (
        <div className="space-y-3 border-t border-border px-4 pb-4 pt-3">
          {item.title && (
            <div>
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Title
              </p>
              <p className="text-sm font-semibold">{item.title}</p>
            </div>
          )}
          {item.hook && (
            <div>
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Hook
              </p>
              <p className="text-sm">{item.hook}</p>
            </div>
          )}
          {item.caption && (
            <div>
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Caption
              </p>
              <p className="whitespace-pre-wrap text-sm">{item.caption}</p>
            </div>
          )}
          {item.cta && (
            <div>
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                CTA
              </p>
              <p className="text-sm italic text-primary">{item.cta}</p>
            </div>
          )}
          {item.hashtags && item.hashtags.length > 0 && (
            <div>
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Hashtags
              </p>
              <p className="text-xs text-muted-foreground">
                {item.hashtags.map((h) => `#${h}`).join(" ")}
              </p>
            </div>
          )}
          <Button
            size="sm"
            variant="outline"
            className="w-full"
            onClick={() => copyText(fullCaption)}
          >
            <Copy className="mr-2 h-3.5 w-3.5" />
            Copy full post
          </Button>
        </div>
      )}
    </div>
  );
}

interface AnalysisPanelProps {
  file: ContentFile;
  onClose: () => void;
}

export function AnalysisPanel({ file, onClose }: AnalysisPanelProps) {
  const hasAnalysis = ["analyzed", "matched", "queued", "posted"].includes(
    file.status
  );

  const { data: analysis, isLoading: analysisLoading } = useGetAnalysis(
    file.id,
    hasAnalysis
  );
  const { data: generated, isLoading: generatedLoading } = useListGenerated(
    file.id,
    file.status === "matched" || file.status === "queued" || file.status === "posted"
  );

  const analyzeFile = useAnalyzeFile();
  const generateCopy = useGenerateCopy();

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-background shadow-2xl">
      {/* Header */}
      <div className="flex items-start justify-between border-b border-border bg-card px-5 py-4">
        <div className="min-w-0">
          <p className="truncate font-semibold">{file.filename}</p>
          <p className="text-xs text-muted-foreground capitalize">
            {file.file_type} · {file.status}
          </p>
        </div>
        <button
          onClick={onClose}
          className="ml-3 rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-accent"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="flex-1 space-y-5 overflow-y-auto p-5">
        {/* Analyze button */}
        {!hasAnalysis && (
          <Button
            className="w-full"
            onClick={() => analyzeFile.mutate(file.id)}
            disabled={analyzeFile.isPending || file.status === "analyzing"}
          >
            <Brain className="mr-2 h-4 w-4" />
            {file.status === "analyzing"
              ? "Analyzing…"
              : analyzeFile.isPending
              ? "Sending to Claude…"
              : "Analyze with Claude"}
          </Button>
        )}

        {/* Analysis results */}
        {analysisLoading && (
          <p className="text-center text-sm text-muted-foreground">
            Loading analysis…
          </p>
        )}

        {analysis && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Brain className="h-4 w-4 text-primary" />
                AI Analysis
                {analysis.model_used && (
                  <Badge variant="outline" className="ml-auto text-xs">
                    {analysis.model_used}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              {analysis.viral_potential_score !== null && (
                <div>
                  <div className="mb-1.5 flex items-center gap-2">
                    <Zap className="h-3.5 w-3.5 text-yellow-500" />
                    <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      Viral potential
                    </span>
                  </div>
                  <ScoreBar score={analysis.viral_potential_score} />
                </div>
              )}

              {analysis.summary && (
                <div>
                  <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Summary
                  </p>
                  <p className="leading-relaxed text-foreground">
                    {analysis.summary}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                {analysis.genre && (
                  <div>
                    <p className="mb-1 text-xs text-muted-foreground">Genre</p>
                    <Badge variant="secondary">{analysis.genre}</Badge>
                  </div>
                )}
                {analysis.category && (
                  <div>
                    <p className="mb-1 text-xs text-muted-foreground">Category</p>
                    <Badge variant="secondary">{analysis.category}</Badge>
                  </div>
                )}
              </div>

              {analysis.emotions && analysis.emotions.length > 0 && (
                <div>
                  <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Emotions
                  </p>
                  <TagList
                    items={analysis.emotions}
                    color="bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300"
                  />
                </div>
              )}

              {analysis.keywords && analysis.keywords.length > 0 && (
                <div>
                  <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Keywords
                  </p>
                  <TagList
                    items={analysis.keywords}
                    color="bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                  />
                </div>
              )}

              {analysis.target_audience && (
                <div>
                  <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Target audience
                  </p>
                  <p className="text-foreground">{analysis.target_audience}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Generate copy */}
        {hasAnalysis && (
          <div>
            <Button
              variant={generated?.length ? "outline" : "default"}
              className="w-full"
              onClick={() => generateCopy.mutate({ fileId: file.id })}
              disabled={generateCopy.isPending}
            >
              <Sparkles className="mr-2 h-4 w-4" />
              {generateCopy.isPending
                ? "Generating…"
                : generated?.length
                ? "Regenerate copy"
                : "Generate platform copy"}
            </Button>
          </div>
        )}

        {/* Generated copy */}
        {generatedLoading && (
          <p className="text-center text-sm text-muted-foreground">
            Loading copy…
          </p>
        )}

        {generated && generated.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Platform copy
            </p>
            {generated.map((item) => (
              <CopyBlock key={item.id} item={item} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
