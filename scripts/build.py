#!/usr/bin/env python3
"""
パッケージビルドスクリプト
"""

import subprocess
import sys
import shutil
import os
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """コマンドを実行し、結果を表示"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command.split(), 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} 完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失敗: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def clean_build_artifacts():
    """ビルド成果物をクリーンアップ"""
    print("🧹 ビルド成果物をクリーンアップ中...")
    
    artifacts = [
        "build",
        "dist", 
        "*.egg-info",
        "src/*.egg-info",
        "__pycache__",
        "src/**/__pycache__",
        "tests/__pycache__",
        "examples/__pycache__",
    ]
    
    for pattern in artifacts:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  削除: {path}")
            elif path.is_file():
                path.unlink()
                print(f"  削除: {path}")
    
    print("✅ クリーンアップ完了")


def main():
    """メイン処理"""
    print("🚀 json-api-builder パッケージビルド開始")
    
    # 1. クリーンアップ
    clean_build_artifacts()
    
    # 2. 依存関係のインストール
    if not run_command("python -m pip install --upgrade pip", "pipのアップグレード"):
        return False
    
    if not run_command("python -m pip install build twine", "ビルドツールのインストール"):
        return False
    
    # 3. テスト実行
    print("\n🧪 テスト実行")
    if not run_command("python -m pytest tests/ -v", "テスト実行"):
        print("⚠️ テストが失敗しましたが、ビルドを続行します")
    
    # 4. パッケージビルド
    print("\n📦 パッケージビルド")
    if not run_command("python -m build", "パッケージビルド"):
        return False
    
    # 5. ビルド結果の確認
    print("\n📋 ビルド結果:")
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
    
    # 6. パッケージの検証
    print("\n🔍 パッケージ検証")
    wheel_files = list(dist_dir.glob("*.whl"))
    if wheel_files:
        wheel_file = wheel_files[0]
        if not run_command(f"python -m twine check {wheel_file}", "パッケージ検証"):
            return False
    
    print("\n🎉 ビルド完了!")
    print("\n📋 次のステップ:")
    print("  - テストPyPIにアップロード: python -m twine upload --repository testpypi dist/*")
    print("  - 本番PyPIにアップロード: python -m twine upload dist/*")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 