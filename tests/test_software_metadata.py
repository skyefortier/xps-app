from app import create_app
from software_metadata import software_metadata


def test_export_source_identity_is_stable_and_injected(tmp_path):
    expected = software_metadata()
    assert expected == software_metadata()
    assert len(expected['source_sha256']) == 64
    assert set(expected['dependencies']) == {'numpy', 'scipy', 'lmfit'}
    with create_app(upload_folder=str(tmp_path)).test_client() as client:
        assert client.get('/api/version').json == expected
        assert expected['source_sha256'] in client.get('/').text
