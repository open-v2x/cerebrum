#   Copyright 99Cloud, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
import asyncio
from scenario_algo.algo_lib import collision_warning


def test_TTC_collsion_prediction():
    his_frames = {
        "ab8756de": [
            {
                "global_track_id": "ab8756de",
                "secMark": 59810,
                "timeStamp": 59810,
                "ptcType": "motor",
                "x": 98,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8756de",
                "secMark": 59860,
                "timeStamp": 59860,
                "ptcType": "motor",
                "x": 98.5,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8756de",
                "secMark": 59910,
                "timeStamp": 59910,
                "ptcType": "motor",
                "x": 99,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8756de",
                "secMark": 59960,
                "timeStamp": 59960,
                "ptcType": "motor",
                "x": 99.5,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
        ],
        "ab8700de": [
            {
                "global_track_id": "ab8700de",
                "secMark": 59810,
                "timeStamp": 59810,
                "ptcType": "motor",
                "x": 86,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8700de",
                "secMark": 59860,
                "timeStamp": 59860,
                "ptcType": "motor",
                "x": 87,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8700de",
                "secMark": 59910,
                "timeStamp": 59910,
                "ptcType": "motor",
                "x": 88,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8700de",
                "secMark": 59960,
                "timeStamp": 59960,
                "ptcType": "motor",
                "x": 89,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
        ],
        "ab12u1i2j": [
            {
                "global_track_id": "ab12u1i2j",
                "secMark": 59810,
                "timeStamp": 59810,
                "ptcType": "motor",
                "x": 200,
                "y": 298,
                "speed": 1000,
                "heading": 0,
            },
            {
                "global_track_id": "ab12u1i2j",
                "secMark": 59860,
                "timeStamp": 59860,
                "ptcType": "motor",
                "x": 200,
                "y": 299,
                "speed": 1000,
                "heading": 0,
            },
            {
                "global_track_id": "ab12u1i2j",
                "secMark": 59910,
                "timeStamp": 59910,
                "ptcType": "motor",
                "x": 200,
                "y": 300,
                "speed": 1000,
                "heading": 0,
            },
            {
                "global_track_id": "ab12u1i2j",
                "secMark": 59960,
                "timeStamp": 59960,
                "ptcType": "motor",
                "x": 200,
                "y": 301,
                "speed": 1000,
                "heading": 0,
            },
        ],
    }
    latest_frame = {
        "ab8756de": {
            "global_track_id": "ab8756de",
            "lat": 1180000000,
            "lon": 310000000,
            "ele": 100,
            "ptcType": "motor",
            "secMark": 10,
            "x": 100,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        "ab8700de": {
            "global_track_id": "ab8700de",
            "lat": 1180000000,
            "lon": 310000000,
            "ele": 100,
            "secMark": 10,
            "ptcType": "motor",
            "x": 90,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        "ab12u1i2j": {
            "global_track_id": "ab12u1i2j",
            "lat": 1180000000,
            "lon": 310000000,
            "ele": 100,
            "secMark": 10,
            "ptcType": "motor",
            "x": 200,
            "y": 302,
            "speed": 1000,
            "heading": 0,
        },
    }
    last_timestamp = 59960
    pred = collision_warning.CollisionWarning(
        v2v_conflict_index=collision_warning.ConflictIndex.TTC
    )
    _, event_list, last_timestamp, _, _ = asyncio.run(
        pred.run(his_frames, latest_frame, last_timestamp)
    )

    assert len(event_list) == 1
    assert event_list[0]["ego"] == "ab8756de"
    assert event_list[0]["other"] == "ab8700de"
    assert (
        event_list[0]["collision_type"]
        == collision_warning.CollisionType.RearEndConflict.value
    )


def test_PSD_collsion_prediction():
    his_frames = {
        "ab8756de": [
            {
                "global_track_id": "ab8756de",
                "secMark": 59810,
                "timeStamp": 59810,
                "ptcType": "motor",
                "x": 98,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8756de",
                "secMark": 59860,
                "timeStamp": 59860,
                "ptcType": "motor",
                "x": 98.5,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8756de",
                "secMark": 59910,
                "timeStamp": 59910,
                "ptcType": "motor",
                "x": 99,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8756de",
                "secMark": 59960,
                "timeStamp": 59960,
                "ptcType": "motor",
                "x": 99.5,
                "y": 100,
                "speed": 500,
                "heading": 7200,
            },
        ],
        "ab8700de": [
            {
                "global_track_id": "ab8700de",
                "secMark": 59810,
                "timeStamp": 59810,
                "ptcType": "motor",
                "x": 86,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8700de",
                "secMark": 59860,
                "timeStamp": 59860,
                "ptcType": "motor",
                "x": 87,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8700de",
                "secMark": 59910,
                "timeStamp": 59910,
                "ptcType": "motor",
                "x": 88,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
            {
                "global_track_id": "ab8700de",
                "secMark": 59960,
                "timeStamp": 59960,
                "ptcType": "motor",
                "x": 89,
                "y": 100,
                "speed": 1000,
                "heading": 7200,
            },
        ],
        "ab12u1i2j": [
            {
                "global_track_id": "ab12u1i2j",
                "secMark": 59810,
                "timeStamp": 59810,
                "ptcType": "motor",
                "x": 200,
                "y": 298,
                "speed": 1000,
                "heading": 0,
            },
            {
                "global_track_id": "ab12u1i2j",
                "secMark": 59860,
                "timeStamp": 59860,
                "ptcType": "motor",
                "x": 200,
                "y": 299,
                "speed": 1000,
                "heading": 0,
            },
            {
                "global_track_id": "ab12u1i2j",
                "secMark": 59910,
                "timeStamp": 59910,
                "ptcType": "motor",
                "x": 200,
                "y": 300,
                "speed": 1000,
                "heading": 0,
            },
            {
                "global_track_id": "ab12u1i2j",
                "secMark": 59960,
                "timeStamp": 59960,
                "ptcType": "motor",
                "x": 200,
                "y": 301,
                "speed": 1000,
                "heading": 0,
            },
        ],
    }
    latest_frame = {
        "ab8756de": {
            "global_track_id": "ab8756de",
            "lat": 1180000000,
            "lon": 310000000,
            "ele": 100,
            "ptcType": "motor",
            "secMark": 10,
            "x": 100,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        "ab8700de": {
            "global_track_id": "ab8700de",
            "lat": 1180000000,
            "lon": 310000000,
            "ele": 100,
            "secMark": 10,
            "ptcType": "motor",
            "x": 90,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        "ab12u1i2j": {
            "global_track_id": "ab12u1i2j",
            "lat": 1180000000,
            "lon": 310000000,
            "ele": 100,
            "secMark": 10,
            "ptcType": "motor",
            "x": 200,
            "y": 302,
            "speed": 1000,
            "heading": 0,
        },
    }
    last_timestamp = 59960

    pred = collision_warning.CollisionWarning(
        v2v_conflict_index=collision_warning.ConflictIndex.PSD
    )
    _, event_list, last_timestamp, _, _ = asyncio.run(
        pred.run(his_frames, latest_frame, last_timestamp)
    )

    assert len(event_list) == 1
    assert event_list[0]["ego"] == "ab8756de"
    assert event_list[0]["other"] == "ab8700de"
    assert (
        event_list[0]["collision_type"]
        == collision_warning.CollisionType.RearEndConflict.value
    )
