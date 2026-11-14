import zipfile, io
def test_html_is_not_zip(tmp_path):
    p = tmp_path / "x.zip"
    p.write_text("<!doctype html><html></html>")
    assert not zipfile.is_zipfile(p)
