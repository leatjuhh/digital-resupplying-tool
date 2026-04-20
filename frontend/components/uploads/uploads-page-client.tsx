"use client"

import Link from "next/link"
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react"
import { CheckCircle2, FileUp, Files, Loader2, RefreshCw, TriangleAlert } from "lucide-react"

import { DashboardHeader } from "@/components/dashboard/dashboard-header"
import { DashboardShell } from "@/components/dashboard/dashboard-shell"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { api, type PDFBatch, type PDFUploadIngestResponse } from "@/lib/api"

function formatDate(value: string) {
  return new Intl.DateTimeFormat("nl-NL", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value))
}

function isPdfFile(file: File) {
  const nameLooksLikePdf = file.name.toLowerCase().endsWith(".pdf")
  const mimeLooksLikePdf = file.type === "application/pdf" || file.type === ""
  return nameLooksLikePdf && mimeLooksLikePdf
}

export function UploadsPageClient() {
  const [batchName, setBatchName] = useState("")
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [fileError, setFileError] = useState<string | null>(null)
  const [pageError, setPageError] = useState<string | null>(null)
  const [successData, setSuccessData] = useState<PDFUploadIngestResponse | null>(null)
  const [recentBatches, setRecentBatches] = useState<PDFBatch[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoadingBatches, setIsLoadingBatches] = useState(true)

  const recentBatchesPreview = useMemo(() => recentBatches.slice(0, 5), [recentBatches])

  async function loadRecentBatches() {
    try {
      setIsLoadingBatches(true)
      const batches = await api.pdf.getBatches()
      setRecentBatches(batches)
      setPageError(null)
    } catch (error) {
      console.error("Failed to fetch recent batches:", error)
      setPageError("Kon recente reeksen niet ophalen. Controleer of de backend actief is.")
    } finally {
      setIsLoadingBatches(false)
    }
  }

  useEffect(() => {
    void loadRecentBatches()
  }, [])

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? [])
    const invalidFiles = files.filter((file) => !isPdfFile(file))

    if (invalidFiles.length > 0) {
      setSelectedFiles([])
      setFileError("Alleen PDF-bestanden zijn toegestaan.")
      return
    }

    setSelectedFiles(files)
    setFileError(null)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (selectedFiles.length === 0) {
      setFileError("Selecteer minimaal een PDF-bestand om te uploaden.")
      return
    }

    if (selectedFiles.some((file) => !isPdfFile(file))) {
      setFileError("De selectie bevat een ongeldig bestandstype.")
      return
    }

    try {
      setIsSubmitting(true)
      setFileError(null)
      setPageError(null)

      const response = await api.pdf.uploadPDFs(
        selectedFiles,
        batchName.trim() || undefined,
      )

      setSuccessData(response)
      setBatchName("")
      setSelectedFiles([])
      await loadRecentBatches()
    } catch (error) {
      console.error("Failed to upload PDFs:", error)
      setPageError(
        error instanceof Error
          ? `Upload mislukt: ${error.message}`
          : "Upload mislukt door een onbekende fout.",
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <DashboardShell>
      <DashboardHeader
        heading="PDF Genereren"
        text="Upload voorraadrapporten en start direct de bestaande voorstelgeneratie."
      />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,1fr)]">
        <Card>
          <CardHeader>
            <CardTitle>Nieuwe upload</CardTitle>
            <CardDescription>
              Voeg een of meer PDF-bestanden toe. Na verwerking kun je direct door naar de gegenereerde reeks.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="grid gap-2">
                <Label htmlFor="batch-name">Batchnaam</Label>
                <Input
                  id="batch-name"
                  placeholder="Bijvoorbeeld Voorraadronde april"
                  value={batchName}
                  onChange={(event) => setBatchName(event.target.value)}
                />
                <p className="text-sm text-muted-foreground">
                  Laat leeg om de backend automatisch een batchnaam te laten genereren.
                </p>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="pdf-files">PDF-bestanden</Label>
                <div className="rounded-lg border border-dashed p-6">
                  <div className="flex items-start gap-3">
                    <div className="rounded-md bg-primary/10 p-2 text-primary">
                      <FileUp className="h-5 w-5" />
                    </div>
                    <div className="flex-1 space-y-3">
                      <div>
                        <p className="font-medium">Selecteer een of meer PDF-bestanden</p>
                        <p className="text-sm text-muted-foreground">
                          Alleen `.pdf` wordt geaccepteerd in deze v1-flow.
                        </p>
                      </div>
                      <Input
                        id="pdf-files"
                        type="file"
                        accept=".pdf,application/pdf"
                        multiple
                        onChange={handleFileChange}
                      />
                    </div>
                  </div>
                </div>
                {selectedFiles.length > 0 && (
                  <div className="rounded-md border bg-muted/30 p-4">
                    <p className="mb-2 text-sm font-medium">
                      {selectedFiles.length} bestand{selectedFiles.length === 1 ? "" : "en"} geselecteerd
                    </p>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {selectedFiles.map((file) => (
                        <li key={`${file.name}-${file.size}`}>{file.name}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {fileError && (
                  <p className="text-sm text-destructive">{fileError}</p>
                )}
              </div>

              <div className="flex flex-wrap gap-3">
                <Button type="submit" disabled={selectedFiles.length === 0 || isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Uploaden...
                    </>
                  ) : (
                    <>
                      <Files className="h-4 w-4" />
                      Upload en genereer
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  disabled={isSubmitting}
                  onClick={() => {
                    setSelectedFiles([])
                    setFileError(null)
                    setSuccessData(null)
                  }}
                >
                  Reset selectie
                </Button>
              </div>
            </form>

            {pageError && (
              <Alert variant="destructive">
                <TriangleAlert className="h-4 w-4" />
                <AlertTitle>Actie mislukt</AlertTitle>
                <AlertDescription>{pageError}</AlertDescription>
              </Alert>
            )}

            {successData && (
              <Alert>
                <CheckCircle2 className="h-4 w-4" />
                <AlertTitle>Upload voltooid</AlertTitle>
                <AlertDescription className="space-y-3">
                  <p>
                    Reeks <strong>#{successData.batch_id}</strong> is aangemaakt met{" "}
                    <strong>{successData.success_count}</strong> succesvolle upload
                    {successData.success_count === 1 ? "" : "s"} en{" "}
                    <strong>{successData.proposals_generated}</strong> gegenereerde voorstellen.
                  </p>
                  <div className="rounded-md border bg-background/70 p-3">
                    <div className="grid gap-1 text-sm">
                      <p>Status: {successData.status}</p>
                      <p>Batchnaam: {successData.batch_name}</p>
                      <p>Totaal bestanden: {successData.total_files}</p>
                      <p>Mislukt: {successData.failed_count}</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {successData.results.map((result) => (
                      <div
                        key={`${result.filename}-${result.status}`}
                        className="rounded-md border bg-background/70 p-3 text-sm"
                      >
                        <p className="font-medium">{result.filename}</p>
                        <p className="text-muted-foreground">
                          Status: {result.status}
                          {typeof result.artikel_count === "number" &&
                            ` · Artikelen: ${result.artikel_count}`}
                        </p>
                        {result.errors && result.errors.length > 0 && (
                          <p className="text-destructive">{result.errors.join(", ")}</p>
                        )}
                      </div>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-3 pt-1">
                    <Button asChild>
                      <Link href={`/proposals/batch/${successData.batch_id}`}>
                        Bekijk reeks
                      </Link>
                    </Button>
                    <Button asChild variant="outline">
                      <Link href="/proposals">Alle voorstellen</Link>
                    </Button>
                  </div>
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-start justify-between space-y-0">
            <div className="space-y-1.5">
              <CardTitle>Recente reeksen</CardTitle>
              <CardDescription>
                Snelle ingang naar de meest recente uploads en proposalreeksen.
              </CardDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={() => void loadRecentBatches()} disabled={isLoadingBatches}>
              <RefreshCw className={`h-4 w-4 ${isLoadingBatches ? "animate-spin" : ""}`} />
              <span className="sr-only">Reeksen verversen</span>
            </Button>
          </CardHeader>
          <CardContent>
            {isLoadingBatches ? (
              <div className="py-6 text-sm text-muted-foreground">Recente reeksen laden...</div>
            ) : recentBatchesPreview.length === 0 ? (
              <div className="py-6 text-sm text-muted-foreground">
                Er zijn nog geen recente reeksen beschikbaar.
              </div>
            ) : (
              <div className="space-y-3">
                {recentBatchesPreview.map((batch) => (
                  <Link
                    key={batch.id}
                    href={`/proposals/batch/${batch.id}`}
                    className="block rounded-lg border p-4 transition-colors hover:bg-accent"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-1">
                        <p className="font-medium">{batch.naam || `Reeks #${batch.id}`}</p>
                        <p className="text-sm text-muted-foreground">
                          Reeks #{batch.id} · {formatDate(batch.created_at)}
                        </p>
                      </div>
                      <span className="rounded-full bg-secondary px-2.5 py-1 text-xs font-medium uppercase tracking-wide text-secondary-foreground">
                        {batch.status}
                      </span>
                    </div>
                    <div className="mt-3 flex gap-4 text-sm text-muted-foreground">
                      <span>{batch.pdf_count} PDF</span>
                      <span>{batch.processed_count} verwerkt</span>
                    </div>
                  </Link>
                ))}
                <Button asChild variant="outline" className="w-full">
                  <Link href="/proposals">Open alle voorstellen</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  )
}
