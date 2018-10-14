import os
import pytest
from pathlib import Path
from cfddns_updater.main import get_global_config_path_if_exists, CONFIG_FILE


def test__get_global_config_path_if_exists__user_wide_path(mocker):
    mock = mocker.patch.object(Path, 'exists', return_value=True)
    assert get_global_config_path_if_exists() == Path(f"~/.{CONFIG_FILE}").expanduser()
    mock.assert_called_once()


@pytest.mark.skipif(os.name != 'posix', reason="Running on a non-posix environment")
def test__get_global_config_path_if_exists__system_wide_path(mocker):
    mock = mocker.patch.object(Path, 'exists', autospec=True,
                               side_effect=lambda self: self.absolute().as_posix() == f"/etc/{CONFIG_FILE}")
    assert get_global_config_path_if_exists() == Path(f"/etc/{CONFIG_FILE}")
    assert mock.call_count == 2
