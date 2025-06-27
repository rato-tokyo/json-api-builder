#!/usr/bin/env python3
"""
テスト実行スクリプト
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """コマンドを実行し、結果を表示"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command.split(), check=True, capture_output=True, text=True
        )
        print(f"✅ {description} 完了")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main():
    """メイン処理"""
    print("🧪 json-api-builder テスト実行")

    # 現在のディレクトリをプロジェクトルートに変更
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    # 1. 依存関係のインストール
    if not run_command(
        "python -m pip install -e .[test]", "テスト依存関係のインストール"
    ):
        return False

    # 2. 基本テスト実行
    print("\n📋 基本テスト実行")
    if not run_command("python -m pytest tests/ -v", "基本テスト"):
        return False

    # 3. カバレッジ付きテスト実行
    print("\n📊 カバレッジ付きテスト実行")
    if not run_command(
        "python -m pytest tests/ --cov=src/json_api_builder --cov-report=term-missing",
        "カバレッジテスト",
    ):
        print("⚠️ カバレッジテストが失敗しましたが、続行します")

    # 4. 型チェック（mypyが利用可能な場合）
    print("\n🔍 型チェック")
    try:
        import importlib.util
        if importlib.util.find_spec("mypy") is not None:
            if not run_command("python -m mypy src/json_api_builder", "型チェック"):
                print("⚠️ 型チェックで警告がありますが、続行します")
        else:
            raise ImportError("mypy not found")
    except ImportError:
        print("⚠️ mypyがインストールされていません。型チェックをスキップします")

    # 5. 使用例のテスト
    print("\n🚀 使用例のテスト")
    examples_dir = project_root / "examples"
    if examples_dir.exists():
        print("使用例ファイルの構文チェック:")
        for example_file in examples_dir.glob("*.py"):
            try:
                with open(example_file, encoding="utf-8") as f:
                    compile(f.read(), example_file, "exec")
                print(f"  ✅ {example_file.name}")
            except SyntaxError as e:
                print(f"  ❌ {example_file.name}: {e}")
                return False

    print("\n🎉 すべてのテストが完了しました!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
