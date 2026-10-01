"""Interactive local credential setup; passwords never become command arguments."""
from __future__ import annotations

import argparse
import getpass
import json
import re
import shutil
import time
from pathlib import Path

from engine.auth import DEFAULT_DEV_ADMIN_EMAIL, UserStore, hash_password


def configure_access(root: Path, email: str, password: str) -> None:
    """Configure first admin or reset an existing local account, preserving 2FA."""
    email = email.strip().casefold()
    if len(email) > 254 or not re.fullmatch(r'[^@\s]+@[^@\s]+', email):
        raise ValueError('Informe um e-mail válido.')
    if len(password) < 12:
        raise ValueError('Use uma senha com pelo menos 12 caracteres.')
    path = Path(root) / '.cerberus' / 'users.json'
    existed = path.exists()
    if existed:
        # Validate before opening UserStore: its legacy corrupt-file fallback seeds
        # a new account; recovery must never overwrite an unreadable user database.
        raw = json.loads(path.read_text(encoding='utf-8'))
        users = raw.get('users') if isinstance(raw, dict) else None
        if not isinstance(users, list) or not users:
            raise ValueError('Cadastro de usuários inválido. Preserve o arquivo e procure suporte.')
        from engine.auth import User
        for user in users:
            if not isinstance(user, dict):
                raise ValueError('Cadastro de usuários inválido.')
            try:
                parsed = User.from_dict(user)
            except (TypeError, KeyError) as exc:
                raise ValueError('Cadastro de usuários inválido.') from exc
            if not isinstance(parsed.email, str) or not isinstance(parsed.password_hash, str):
                raise ValueError('Cadastro de usuários inválido.')
        if not any(str(user.get('email', '')).casefold() == email for user in users):
            raise ValueError('E-mail não cadastrado. Use uma conta existente neste computador.')
        folder = path.parent / 'backups'
        folder.mkdir(exist_ok=True)
        shutil.copy2(path, folder / f'users-before-access-{time.time_ns()}.json')
    store = UserStore(path, default_email=email, default_password=password)
    if existed:
        store.set_password(email, hash_password(password))


def main() -> int:
    parser = argparse.ArgumentParser(description='Configurar o acesso local ao Cerberus.')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print('Configurar acesso ao Cerberus\nA senha será digitada localmente e não aparecerá na tela.')
    print('Se já existir uma conta, sua senha será redefinida e o 2FA será preservado.')
    email = input(f'E-mail [{DEFAULT_DEV_ADMIN_EMAIL}]: ').strip() or DEFAULT_DEV_ADMIN_EMAIL
    password = getpass.getpass('Nova senha (mínimo 12 caracteres): ')
    confirm = getpass.getpass('Confirme a senha: ')
    if password != confirm:
        print('As senhas não coincidem. Nenhuma alteração foi feita.')
        return 1
    try:
        configure_access(args.root, email, password)
    except (ValueError, OSError, KeyError) as exc:
        print(f'Não foi possível configurar o acesso: {exc}')
        return 1
    print('Acesso configurado. Reinicie o painel e entre com o e-mail e a senha definidos.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
