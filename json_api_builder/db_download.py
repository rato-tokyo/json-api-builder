"""
データベースファイルダウンロード機能

APIBuilderにデータベースファイルのダウンロードエンドポイントを追加する機能を提供します。
"""

import os
from datetime import datetime

from fastapi import HTTPException
from fastapi.responses import FileResponse


class DBDownloadMixin:
    """データベースダウンロード機能を提供するMixin"""

    def add_db_download_endpoint(
        self,
        endpoint_path: str = "/download/database",
        require_auth: bool = False,
        auth_token: str | None = None,
    ) -> None:
        """
        データベースファイルのダウンロードエンドポイントを追加

        Args:
            endpoint_path: エンドポイントのパス
            require_auth: 認証を必要とするか
            auth_token: 認証に使用するトークン（require_auth=Trueの場合必須）
        """

        @self.app.get(endpoint_path)
        async def download_database(token: str | None = None):
            """データベースファイルをダウンロード"""

            # 認証チェック
            if require_auth:
                if not auth_token:
                    raise HTTPException(
                        status_code=500, detail="Authentication token not configured"
                    )
                if token != auth_token:
                    raise HTTPException(
                        status_code=401, detail="Invalid authentication token"
                    )

            # データベースファイルの存在確認
            db_path = self._get_db_file_path()
            if not os.path.exists(db_path):
                raise HTTPException(status_code=404, detail="Database file not found")

            # ファイルサイズチェック
            file_size = os.path.getsize(db_path)
            if file_size == 0:
                raise HTTPException(status_code=404, detail="Database file is empty")

            # ダウンロード用のファイル名を生成（タイムスタンプ付き）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            download_filename = f"database_backup_{timestamp}.db"

            return FileResponse(
                path=db_path,
                filename=download_filename,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f"attachment; filename={download_filename}",
                    "Content-Length": str(file_size),
                },
            )

    def _get_db_file_path(self) -> str:
        """データベースファイルのパスを取得"""
        # SQLAlchemyのengine URLからファイルパスを抽出
        url_str = str(self.engine.url)
        if url_str.startswith("sqlite:///"):
            return url_str[10:]  # "sqlite:///" を除去
        else:
            raise HTTPException(
                status_code=500,
                detail="Database download is only supported for SQLite databases",
            )


def add_download_info_endpoint(app, db_path: str):
    """ダウンロード情報を表示するエンドポイントを追加（デバッグ用）"""

    @app.get("/download/info")
    async def download_info():
        """データベースファイルの情報を取得"""
        if not os.path.exists(db_path):
            return {
                "exists": False,
                "path": db_path,
                "message": "Database file not found",
            }

        stat = os.stat(db_path)
        return {
            "exists": True,
            "path": db_path,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "download_url": "/download/database",
        }
