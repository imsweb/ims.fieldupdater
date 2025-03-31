import pytest

PACKAGE_NAME = "ims.fieldupdater"


class TestSetupUninstall:
    @pytest.fixture(autouse=True)
    def uninstalled(self, installer):
        installer.uninstall_product(PACKAGE_NAME)

    def test_addon_uninstalled(self, installer):
        """Test if package is uninstalled."""
        assert installer.is_product_installed(PACKAGE_NAME) is False
