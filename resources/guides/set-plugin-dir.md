# ABRA_PLUGIN_DIR 셋팅 

오케스트레이터는 실행 시작 시 다음 순서로 `{ABRA_PLUGIN_DIR}`를 결정:
1. 아래 후보 경로 중 존재하는 첫 번째를 `PLUGIN_BASE_DIR`로 선택
   - `/mnt/.local-plugins/cache/unicorn/dmap` (Cowork VM)
   - `~/.claude/plugins/cache/unicorn/dmap` (Mac/Linux CLI)
   - `%APPDATA%/Claude/plugins/cache/unicorn/dmap` (Windows CLI)
2. `PLUGIN_BASE_DIR` 하위의 버전 디렉토리를 시맨틱 버전 비교하여 최신 버전 선택
3. 해당 디렉토리의 절대 경로를 `{ABRA_PLUGIN_DIR}`에 바인딩
4. 이후 모든 `{ABRA_PLUGIN_DIR}/...` 경로를 절대 경로로 치환하여 파일을 읽음
5. 현재 프로젝트의 CLAUDE.md에 {ABRA_PLUGIN_DIR}값이 다르면 업데이트함   
   ```
   ## ABRA_PLUGIN_DIR
   {ABRA_PLUGIN_DIR}={경로}
   ```

   