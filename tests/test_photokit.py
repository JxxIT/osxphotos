""" test photokit.py methods """

import os
import pathlib
import tempfile

import pytest

from osxphotos.platform import is_macos

if is_macos:
    from osxphotos.photokit import (
        PHOTOS_VERSION_CURRENT,
        PHOTOS_VERSION_ORIGINAL,
        PHOTOS_VERSION_UNADJUSTED,
        LivePhotoAsset,
        PhotoAsset,
        PhotoLibrary,
        VideoAsset,
    )
else:
    pytest.skip(allow_module_level=True)

skip_test = "OSXPHOTOS_TEST_EXPORT" not in os.environ
pytestmark = pytest.mark.skipif(
    skip_test, reason="Skip if not running with author's personal library."
)


UUID_DICT = {
    "plain_photo": {
        "uuid": "C07BB1E1-2F61-4263-AB8E-943FD47CF013",
        "filename": "IMG_8844.JPG",
    },
    "hdr": {"uuid": "7D852FC8-EA03-49C9-96F7-B049CE44A7EA", "filename": "IMG_6162.JPG"},
    "selfie": {
        "uuid": "F21DFA19-E3E8-4610-8401-0447345F3074",
        "filename": "IMG_1929.JPG",
    },
    "video": {
        "uuid": "A6F31CC4-213B-4F27-85FD-7DD81AF1ED09",
        "filename": "IMG_9411.TRIM.MOV",
    },
    "hasadjustments": {
        "uuid": "1D99D83D-F820-4D30-A831-7B45BDF294D3",
        "filename": "IMG_2860.JPG",
        "adjusted_size": 3012634,
        "unadjusted_size": 2580058,
    },
    "slow_mo": {
        "uuid": "1B3FC526-9D27-48A1-A39D-47C5E1F0633C",
        "filename": "IMG_4055.MOV",
    },
    "live_photo": {
        "uuid": "03EE6CE2-20E6-489D-A149-A2EC7D11C70A",
        "filename": "IMG_3259.HEIC",
        "filename_video": "IMG_3259.mov",
    },
    "burst": {
        "uuid": "A9BC0824-1200-4B6F-A071-779E1C555465",
        "filename": "IMG_8196.JPG",
        "burst_selected": 4,
        "burst_all": 5,
    },
    "raw+jpeg": {
        "uuid": "3C973493-7109-40E9-BF8D-6476AE7C8001",
        "filename": "IMG_1994.JPG",
        "raw_filename": "IMG_1994.CR2",
        "unadjusted_size": 16128420,
        "uti_raw": "com.canon.cr2-raw-image",
        "uti": "public.jpeg",
    },
}


def test_fetch_uuid():
    """test fetch_uuid"""
    uuid = UUID_DICT["plain_photo"]["uuid"]
    filename = UUID_DICT["plain_photo"]["filename"]

    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)
    assert isinstance(photo, PhotoAsset)


def test_plain_photo():
    """test plain_photo"""
    uuid = UUID_DICT["plain_photo"]["uuid"]
    filename = UUID_DICT["plain_photo"]["filename"]

    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)
    assert photo.original_filename == filename
    assert photo.raw_filename is None
    assert photo.isphoto
    assert not photo.ismovie


def test_raw_plus_jpeg():
    """test RAW+JPEG"""
    uuid = UUID_DICT["raw+jpeg"]["uuid"]

    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)
    assert photo.original_filename == UUID_DICT["raw+jpeg"]["filename"]
    assert photo.raw_filename == UUID_DICT["raw+jpeg"]["raw_filename"]
    assert photo.uti_raw() == UUID_DICT["raw+jpeg"]["uti_raw"]
    assert photo.uti() == UUID_DICT["raw+jpeg"]["uti"]


def test_hdr():
    """test hdr"""
    uuid = UUID_DICT["hdr"]["uuid"]
    filename = UUID_DICT["hdr"]["filename"]

    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)
    assert photo.original_filename == filename
    assert photo.hdr


def test_burst():
    """test burst and burstid"""
    test_dict = UUID_DICT["burst"]
    uuid = test_dict["uuid"]
    filename = test_dict["filename"]

    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)
    assert photo.original_filename == filename
    assert photo.burst
    assert photo.burstid


# def test_selfie():
#     """ test selfie """
#     uuid = UUID_DICT["selfie"]["uuid"]
#     filename = UUID_DICT["selfie"]["filename"]

#     lib = PhotoLibrary()
#     photo = lib.fetch_uuid(uuid)
#     assert photo.original_filename == filename
#     assert photo.selfie


def test_video():
    """test ismovie"""
    uuid = UUID_DICT["video"]["uuid"]
    filename = UUID_DICT["video"]["filename"]

    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)
    assert isinstance(photo, VideoAsset)
    assert photo.original_filename == filename
    assert photo.ismovie
    assert not photo.isphoto


def test_slow_mo():
    """test slow_mo"""
    test_dict = UUID_DICT["slow_mo"]
    uuid = test_dict["uuid"]
    filename = test_dict["filename"]

    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)
    assert isinstance(photo, VideoAsset)
    assert photo.original_filename == filename
    assert photo.ismovie
    assert photo.slow_mo
    assert not photo.isphoto


### PhotoAsset


def test_export_photo_original():
    """test PhotoAsset.export"""
    test_dict = UUID_DICT["hasadjustments"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_ORIGINAL)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem
        assert export_path.stat().st_size == test_dict["unadjusted_size"]


def test_export_photo_unadjusted():
    """test PhotoAsset.export"""
    test_dict = UUID_DICT["hasadjustments"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_UNADJUSTED)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem
        assert export_path.stat().st_size == test_dict["unadjusted_size"]


def test_export_photo_current():
    """test PhotoAsset.export"""
    test_dict = UUID_DICT["hasadjustments"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem
        assert export_path.stat().st_size == test_dict["adjusted_size"]


def test_export_photo_raw():
    """test PhotoAsset.export for raw component"""
    test_dict = UUID_DICT["raw+jpeg"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, raw=True)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["raw_filename"]
        assert export_path.stem == pathlib.Path(filename).stem
        assert export_path.stat().st_size == test_dict["unadjusted_size"]


### VideoAsset


def test_export_video_original():
    """test VideoAsset.export"""
    test_dict = UUID_DICT["video"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_ORIGINAL)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem


def test_export_video_unadjusted():
    """test VideoAsset.export"""
    test_dict = UUID_DICT["video"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_UNADJUSTED)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem


def test_export_video_current():
    """test VideoAsset.export"""
    test_dict = UUID_DICT["video"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_CURRENT)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem


### Slow-Mo VideoAsset


@pytest.mark.skip(reason="Slow-mo videos not working, #1286")
def test_export_slow_mo_original():
    """test VideoAsset.export for slow mo video"""
    test_dict = UUID_DICT["slow_mo"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_ORIGINAL)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem


@pytest.mark.skip(reason="Slow-mo videos not working, #1286")
def test_export_slow_mo_unadjusted():
    """test VideoAsset.export for slow mo video"""
    test_dict = UUID_DICT["slow_mo"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_UNADJUSTED)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem


@pytest.mark.skip(reason="Slow-mo videos not working, #1286")
def test_export_slow_mo_current():
    """test VideoAsset.export for slow mo video"""
    test_dict = UUID_DICT["slow_mo"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_CURRENT)
        export_path = pathlib.Path(export_path[0])
        assert export_path.is_file()
        filename = test_dict["filename"]
        assert export_path.stem == pathlib.Path(filename).stem


### LivePhotoAsset


def test_export_live_original():
    """test LivePhotoAsset.export"""
    test_dict = UUID_DICT["live_photo"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_ORIGINAL)
        for f in export_path:
            filepath = pathlib.Path(f)
            assert filepath.is_file()
            filename = test_dict["filename"]
            assert filepath.stem == pathlib.Path(filename).stem


def test_export_live_unadjusted():
    """test LivePhotoAsset.export"""
    test_dict = UUID_DICT["live_photo"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_UNADJUSTED)
        for file in export_path:
            filepath = pathlib.Path(file)
            assert filepath.is_file()
            filename = test_dict["filename"]
            assert filepath.stem == pathlib.Path(filename).stem


def test_export_live_current():
    """test LivePhotAsset.export"""
    test_dict = UUID_DICT["live_photo"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, version=PHOTOS_VERSION_CURRENT)
        for file in export_path:
            filepath = pathlib.Path(file)
            assert filepath.is_file()
            filename = test_dict["filename"]
            assert filepath.stem == pathlib.Path(filename).stem


def test_export_live_current_just_photo():
    """test LivePhotAsset.export"""
    test_dict = UUID_DICT["live_photo"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, photo=True, video=False)
        assert len(export_path) == 1
        assert export_path[0].lower().endswith(".heic")


def test_export_live_current_just_video():
    """test LivePhotAsset.export"""
    test_dict = UUID_DICT["live_photo"]
    uuid = test_dict["uuid"]
    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)

    with tempfile.TemporaryDirectory(prefix="photokit_test") as tempdir:
        export_path = photo.export(tempdir, photo=False, video=True)
        assert len(export_path) == 1
        assert export_path[0].lower().endswith(".mov")


def test_fetch_burst_uuid():
    """test fetch_burst_uuid"""
    test_dict = UUID_DICT["burst"]
    uuid = test_dict["uuid"]
    filename = test_dict["filename"]

    lib = PhotoLibrary()
    photo = lib.fetch_uuid(uuid)
    bursts_selected = lib.fetch_burst_uuid(photo.burstid)
    assert len(bursts_selected) == test_dict["burst_selected"]
    assert isinstance(bursts_selected[0], PhotoAsset)

    bursts_all = lib.fetch_burst_uuid(photo.burstid, all=True)
    assert len(bursts_all) == test_dict["burst_all"]
    assert isinstance(bursts_all[0], PhotoAsset)
