import unittest

from shared.updater import select_asset_url


class UpdaterAssetSelectionTests(unittest.TestCase):
    def test_select_asset_url_prefers_exact_linux_binary_and_ignores_flatpak(self):
        release = {
            "assets": [
                {
                    "name": "Skakavi-Krompir-Linux-amd64",
                    "browser_download_url": "https://example.test/linux-amd64",
                },
                {
                    "name": "Skakavi-Krompir-Linux_2.1.1_amd64.flatpak",
                    "browser_download_url": "https://example.test/linux.flatpak",
                },
            ]
        }

        self.assertEqual(
            select_asset_url(release, "Skakavi-Krompir-Linux-amd64"),
            "https://example.test/linux-amd64",
        )


if __name__ == "__main__":
    unittest.main()
