class TestSetupInstall:
    def test_addon_installed(self, installer):
        assert installer.is_product_installed("ims.fieldupdater") is True

    def test_profile(self, setup_tool):
        vrs = setup_tool.getLastVersionForProfile("ims.fieldupdater:default")
        assert vrs != "unknown"
