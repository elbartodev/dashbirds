# subscription.py
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, flash

# Importar db e modelos depois (para evitar circular import)
# Usage: from subscription import requer_plano, gerar_chave_licenca

PLANOS = {
    "gratuito": {
        "nome": {"pt": "Gratuito", "en": "Free", "fr": "Gratuit", "de": "Kostenlos"},
        "limite_aves": 10,
        "cruzamentos": False,
        "calculadora_alimentacao": False,
        "exportacao": False,
        "prioridade_suporte": False,
        "preco_anual": 0,
    },
    "anual": {
        "nome": {"pt": "Anual", "en": "Annual", "fr": "Annuel", "de": "Jährlich"},
        "limite_aves": 999999,
        "cruzamentos": True,
        "calculadora_alimentacao": True,
        "exportacao": True,
        "prioridade_suporte": True,
        "preco_anual": 197.00,
    }
}


def gerar_chave_licenca():
    """Gera uma chave de licença no formato XXXX-XXXX-XXXX-XXXX"""
    chars = string.ascii_uppercase + string.digits
    grupos = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
    return '-'.join(grupos)


def hash_chave(chave):
    return hashlib.sha256(chave.encode()).hexdigest()


def verificar_plano_usuario(usuario_id, db, Assinatura):
    """Verifica o plano ativo do usuário."""
    assinatura = Assinatura.query.filter_by(
        usuario_id=usuario_id, ativo=True
    ).first()

    if not assinatura:
        return "gratuito"

    if assinatura.validade and assinatura.validade < datetime.utcnow():
        assinatura.ativo = False
        db.session.commit()
        return "gratuito"

    return assinatura.plano


def tem_acesso(usuario_id, recurso, db, Assinatura):
    """Verifica se o usuário tem acesso a um recurso específico."""
    plano = verificar_plano_usuario(usuario_id, db, Assinatura)
    return PLANOS[plano].get(recurso, False)


def requer_plano_anual(f):
    """Decorator para rotas que exigem plano anual."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        from app import db, Assinatura
        plano = verificar_plano_usuario(session["usuario_id"], db, Assinatura)
        if plano != "anual":
            flash("Esta funcionalidade requer o plano anual.", "warning")
            return redirect(url_for("planos"))
        return f(*args, **kwargs)
    return decorated_function