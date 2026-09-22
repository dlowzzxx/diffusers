# Copyright 2026 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

from utils import check_ai


def test_main_reads_ai_files_as_utf8(tmp_path, monkeypatch):
    ai_dir = tmp_path / ".ai"
    references_dir = ai_dir / "references"
    skill_dir = ai_dir / "skills" / "demo"
    references_dir.mkdir(parents=True)
    skill_dir.mkdir(parents=True)

    marker = "\u201d"
    guide = references_dir / "guide.md"
    skill = skill_dir / "SKILL.md"
    guide.write_bytes(f"# Guide {marker}\n".encode("utf-8"))
    skill.write_bytes(
        f"---\nname: demo\ndescription: A demo skill.\n---\n\nSee references/guide.md. {marker}\n".encode("utf-8")
    )

    monkeypatch.setattr(check_ai, "AI_DIR", ai_dir)
    monkeypatch.setattr(check_ai, "REFERENCES_DIR", references_dir)

    original_read_text = Path.read_text
    reads = []

    def read_text(path, *args, **kwargs):
        encoding = kwargs.get("encoding", args[0] if args else None)
        reads.append((path, encoding))
        if not args and "encoding" not in kwargs:
            kwargs["encoding"] = "cp1252"
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)

    assert check_ai.main() == 0
    assert [path for path, _ in reads] == [guide, skill, guide, skill]
    assert all(encoding == "utf-8" for _, encoding in reads)
