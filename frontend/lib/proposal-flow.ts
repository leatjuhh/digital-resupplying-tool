import type { Proposal, ProposalMove } from "@/lib/api"

export interface BatchFlowInfo {
  totalProposals: number
  assessedProposals: number
  name: string
  currentIndex: number
  nextProposalId?: string
}

interface EditableStore {
  id: string
  name: string
  inventoryCurrent: number[]
  inventoryProposed: number[]
}

interface EditableProposalData {
  sizes: string[]
  stores: EditableStore[]
}

export function buildBatchFlowInfo(
  batchName: string,
  proposals: Proposal[],
  proposalId: number,
): BatchFlowInfo | undefined {
  if (!proposals.length) {
    return undefined
  }

  const currentIndex = proposals.findIndex((proposal) => proposal.id === proposalId)
  if (currentIndex === -1) {
    return undefined
  }

  const nextProposal = proposals[currentIndex + 1]

  return {
    totalProposals: proposals.length,
    assessedProposals: currentIndex,
    name: batchName,
    currentIndex,
    nextProposalId: nextProposal ? nextProposal.id.toString() : undefined,
  }
}

export function buildMovesFromEditableProposal(data: EditableProposalData): ProposalMove[] {
  const moves: ProposalMove[] = []

  data.sizes.forEach((size, sizeIndex) => {
    const sources = data.stores
      .map((store) => ({
        id: store.id,
        name: store.name,
        qty: Math.max(0, store.inventoryCurrent[sizeIndex] - store.inventoryProposed[sizeIndex]),
      }))
      .filter((store) => store.qty > 0)

    const destinations = data.stores
      .map((store) => ({
        id: store.id,
        name: store.name,
        qty: Math.max(0, store.inventoryProposed[sizeIndex] - store.inventoryCurrent[sizeIndex]),
      }))
      .filter((store) => store.qty > 0)

    let sourceIndex = 0
    let destinationIndex = 0

    while (sourceIndex < sources.length && destinationIndex < destinations.length) {
      const source = sources[sourceIndex]
      const destination = destinations[destinationIndex]
      const qty = Math.min(source.qty, destination.qty)

      moves.push({
        size,
        from_store: source.id,
        from_store_name: source.name,
        to_store: destination.id,
        to_store_name: destination.name,
        qty,
        score: 0,
        reason: "Handmatige aanpassing vanuit proposal edit",
        from_bv: "",
        to_bv: "",
      })

      source.qty -= qty
      destination.qty -= qty

      if (source.qty === 0) {
        sourceIndex += 1
      }

      if (destination.qty === 0) {
        destinationIndex += 1
      }
    }
  })

  return moves
}
