#!/usr/bin/env python3
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

CONTENTTYPE_BY_EXTENSION = {
    # Docs
    'csv': 'text/csv',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'pdf': 'application/pdf',
    # Images
    'bmp': 'image/bmp',
    'gif': 'image/gif',
    'heic': 'image/heic',
    'heif': 'image/heif',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    # Videos
    'mkv': 'video/x-matroska',
    'mp4': 'video/mp4',
    'webm': 'video/webm',
}

JSON_IDENTATION = 2

S3_URL_EXPIRATION_SECONDS = 60
