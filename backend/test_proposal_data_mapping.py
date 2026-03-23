import unittest
from types import SimpleNamespace

from routers.pdf_ingest import (
    OPTIMAL_DISTRIBUTION_RULE,
    collect_store_inventory,
    is_optimal_distribution_proposal,
)


class ProposalDataMappingTests(unittest.TestCase):
    def test_collect_store_inventory_keeps_verkocht_as_store_total(self):
        records = [
            SimpleNamespace(filiaal_code="5", filiaal_naam="Panningen", maat="S", voorraad=2, verkocht=6),
            SimpleNamespace(filiaal_code="5", filiaal_naam="Panningen", maat="M", voorraad=1, verkocht=0),
            SimpleNamespace(filiaal_code="8", filiaal_naam="Weert", maat="S", voorraad=1, verkocht=3),
        ]

        stores_inventory, all_sizes = collect_store_inventory(records)

        self.assertEqual(sorted(all_sizes), ["M", "S"])
        self.assertEqual(stores_inventory["5"]["sizes"], {"S": 2, "M": 1})
        self.assertEqual(stores_inventory["5"]["sold_total"], 6)
        self.assertEqual(stores_inventory["8"]["sold_total"], 3)

    def test_optimal_distribution_requires_explicit_backend_signal(self):
        optimal = SimpleNamespace(
            moves=[],
            applied_rules=["Situation: MEDIUM_STOCK", OPTIMAL_DISTRIBUTION_RULE],
            reason="Dit artikel is reeds optimaal verdeeld.",
        )
        no_moves_without_signal = SimpleNamespace(
            moves=[],
            applied_rules=[],
            reason="Geen mutaties gevonden.",
        )
        with_moves = SimpleNamespace(
            moves=[{"size": "M"}],
            applied_rules=[OPTIMAL_DISTRIBUTION_RULE],
            reason="Dit artikel is reeds optimaal verdeeld.",
        )

        self.assertTrue(is_optimal_distribution_proposal(optimal))
        self.assertFalse(is_optimal_distribution_proposal(no_moves_without_signal))
        self.assertFalse(is_optimal_distribution_proposal(with_moves))


if __name__ == "__main__":
    unittest.main()
