import os
from datetime import datetime, date
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ═══════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dashbirds-secret-2025')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'dashbirds.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ═══════════════════════════════════════════
# MODELOS
# ═══════════════════════════════════════════

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id            = db.Column(db.Integer, primary_key=True)
    nome          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash    = db.Column(db.String(256), nullable=False)
    criadouro     = db.Column(db.String(120), default='')
    documento     = db.Column(db.String(30), default='')
    telefone      = db.Column(db.String(30), default='')
    lang          = db.Column(db.String(5), default='pt')
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)

    aves          = db.relationship('Ave', backref='usuario', lazy=True)
    gaiolas       = db.relationship('Gaiola', backref='usuario', lazy=True)
    posturas      = db.relationship('Postura', backref='usuario', lazy=True)
    vendas        = db.relationship('Venda', backref='usuario', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Gaiola(db.Model):
    __tablename__ = 'gaiola'
    id            = db.Column(db.Integer, primary_key=True)
    usuario_id    = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nome          = db.Column(db.String(80), nullable=False)
    tipo          = db.Column(db.String(50), default='Reprodução')
    capacidade    = db.Column(db.Integer, default=2)
    localizacao   = db.Column(db.String(80), default='')
    observacoes   = db.Column(db.Text, default='')

    aves          = db.relationship('Ave', backref='gaiola', lazy=True)


class Ave(db.Model):
    __tablename__ = 'ave'
    id                    = db.Column(db.Integer, primary_key=True)
    usuario_id            = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    gaiola_id             = db.Column(db.Integer, db.ForeignKey('gaiola.id'), nullable=True)
    anilha                = db.Column(db.String(40), nullable=False)
    cor_anilha            = db.Column(db.String(10), default='#52b788')
    especie               = db.Column(db.String(80), default='')
    subespecie            = db.Column(db.String(80), default='')
    sexo                  = db.Column(db.String(20), default='Indeterminado')
    cor_plumagem          = db.Column(db.String(60), default='')
    genetica              = db.Column(db.String(120), default='')
    data_nascimento       = db.Column(db.Date, nullable=True)
    data_aquisicao        = db.Column(db.Date, nullable=True)
    custo_aquisicao       = db.Column(db.Float, default=0.0)
    custo_alimentacao_mes = db.Column(db.Float, default=0.0)
    valor_venda           = db.Column(db.Float, default=0.0)
    status                = db.Column(db.String(30), default='Ativo')
    origem                = db.Column(db.String(40), default='Comprado')
    observacoes           = db.Column(db.Text, default='')
    criado_em             = db.Column(db.DateTime, default=datetime.utcnow)

    posturas_mae  = db.relationship('Postura', foreign_keys='Postura.femea_id', backref='femea', lazy=True)
    posturas_pai  = db.relationship('Postura', foreign_keys='Postura.macho_id', backref='macho', lazy=True)
    filhotes_mae  = db.relationship('Filhote', foreign_keys='Filhote.femea_id', backref='femea', lazy=True)
    filhotes_pai  = db.relationship('Filhote', foreign_keys='Filhote.macho_id', backref='macho', lazy=True)
    venda         = db.relationship('Venda', backref='ave', uselist=False, lazy=True)

    def custo_total(self):
        custo = self.custo_aquisicao or 0.0
        if self.custo_alimentacao_mes and self.data_aquisicao:
            meses = max(1, (date.today() - self.data_aquisicao).days // 30)
            custo += self.custo_alimentacao_mes * meses
        return round(custo, 2)


class Postura(db.Model):
    __tablename__ = 'postura'
    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    femea_id        = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    macho_id        = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    gaiola_id       = db.Column(db.Integer, db.ForeignKey('gaiola.id'), nullable=True)
    data_postura    = db.Column(db.Date, nullable=True)
    total_ovos      = db.Column(db.Integer, default=0)
    ovos_fecundados = db.Column(db.Integer, default=0)
    ovos_eclodidos  = db.Column(db.Integer, default=0)
    status          = db.Column(db.String(30), default='Em andamento')
    observacoes     = db.Column(db.Text, default='')
    criado_em       = db.Column(db.DateTime, default=datetime.utcnow)

    filhotes  = db.relationship('Filhote', backref='postura', lazy=True)
    gaiola_p  = db.relationship('Gaiola', foreign_keys=[gaiola_id], lazy=True)


class Filhote(db.Model):
    __tablename__ = 'filhote'
    id            = db.Column(db.Integer, primary_key=True)
    usuario_id    = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    postura_id    = db.Column(db.Integer, db.ForeignKey('postura.id'), nullable=True)
    femea_id      = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    macho_id      = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    especie       = db.Column(db.String(80), default='')
    sexo          = db.Column(db.String(20), default='Indeterminado')
    anilha        = db.Column(db.String(40), default='')
    cor_anilha    = db.Column(db.String(10), default='#52b788')
    genetica      = db.Column(db.String(120), default='')
    valor_venda   = db.Column(db.Float, default=0.0)
    data_eclosao  = db.Column(db.Date, nullable=True)
    status        = db.Column(db.String(30), default='No berçário')
    observacoes   = db.Column(db.Text, default='')
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)


class Venda(db.Model):
    __tablename__ = 'venda'
    id          = db.Column(db.Integer, primary_key=True)
    usuario_id  = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ave_id      = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    data_venda  = db.Column(db.Date, nullable=True)
    valor       = db.Column(db.Float, default=0.0)
    comprador   = db.Column(db.String(120), default='')
    contato     = db.Column(db.String(120), default='')
    observacoes = db.Column(db.Text, default='')
    criado_em   = db.Column(db.DateTime, default=datetime.utcnow)
    # ═══════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════

def get_lang():
    """Retorna o idioma atual da sessão ou do usuário logado."""
    return session.get('lang', 'pt')


def login_required(f):
    """Decorator que exige login para acessar a rota."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_usuario():
    """Retorna o usuário logado ou None."""
    uid = session.get('usuario_id')
    if uid:
        return Usuario.query.get(uid)
    return None


@app.context_processor
def inject_globals():
    """Injeta variáveis globais em todos os templates."""
    return {
        'lang':    get_lang(),
        'session': session,
    }


def parse_date(value):
    """Converte string 'YYYY-MM-DD' para date ou None."""
    if value:
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            pass
    return None


def parse_float(value, default=0.0):
    """Converte string para float com fallback."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_int(value, default=0):
    """Converte string para int com fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ═══════════════════════════════════════════
# IDIOMA
# ═══════════════════════════════════════════

@app.route('/lang/<codigo>')
def set_lang(codigo):
    """Troca o idioma da sessão e salva no perfil se logado."""
    if codigo in ('pt', 'en', 'fr', 'de'):
        session['lang'] = codigo
        u = get_usuario()
        if u:
            u.lang = codigo
            db.session.commit()
    return redirect(request.referrer or url_for('dashboard'))


# ═══════════════════════════════════════════
# AUTH — LOGIN / CADASTRO / LOGOUT
# ═══════════════════════════════════════════

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))

    erro = None
    lang = get_lang()

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        u = Usuario.query.filter_by(email=email).first()

        if not u or not u.check_senha(senha):
            erros = {
                'pt': 'E-mail ou senha incorretos.',
                'en': 'Incorrect email or password.',
                'fr': 'E-mail ou mot de passe incorrect.',
                'de': 'E-Mail oder Passwort falsch.',
            }
            erro = erros.get(lang, erros['pt'])
        else:
            session['usuario_id'] = u.id
            session['nome']       = u.nome
            session['lang']       = u.lang or 'pt'
            return redirect(url_for('dashboard'))

    return render_template('login.html', erro=erro, lang=lang)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))

    erro = None
    lang = get_lang()

    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        email     = request.form.get('email', '').strip().lower()
        senha     = request.form.get('senha', '')
        senha2    = request.form.get('senha2', '')
        criadouro = request.form.get('criadouro', '').strip()
        documento = request.form.get('documento', '').strip()
        telefone  = request.form.get('telefone', '').strip()

        erros = {
            'campos': {
                'pt': 'Preencha todos os campos obrigatórios.',
                'en': 'Fill in all required fields.',
                'fr': 'Remplissez tous les champs obligatoires.',
                'de': 'Füllen Sie alle Pflichtfelder aus.',
            },
            'senha': {
                'pt': 'As senhas não coincidem.',
                'en': 'Passwords do not match.',
                'fr': 'Les mots de passe ne correspondent pas.',
                'de': 'Passwörter stimmen nicht überein.',
            },
            'curta': {
                'pt': 'A senha deve ter pelo menos 6 caracteres.',
                'en': 'Password must have at least 6 characters.',
                'fr': 'Le mot de passe doit avoir au moins 6 caractères.',
                'de': 'Passwort muss mindestens 6 Zeichen haben.',
            },
            'email': {
                'pt': 'Este e-mail já está cadastrado.',
                'en': 'This email is already registered.',
                'fr': 'Cet e-mail est déjà enregistré.',
                'de': 'Diese E-Mail ist bereits registriert.',
            },
        }

        if not nome or not email or not senha:
            erro = erros['campos'].get(lang)
        elif senha != senha2:
            erro = erros['senha'].get(lang)
        elif len(senha) < 6:
            erro = erros['curta'].get(lang)
        elif Usuario.query.filter_by(email=email).first():
            erro = erros['email'].get(lang)
        else:
            u = Usuario(
                nome=nome,
                email=email,
                criadouro=criadouro,
                documento=documento,
                telefone=telefone,
                lang=lang,
            )
            u.set_senha(senha)
            db.session.add(u)
            db.session.commit()
            session['usuario_id'] = u.id
            session['nome']       = u.nome
            session['lang']       = u.lang
            return redirect(url_for('dashboard'))

    return render_template('cadastro.html', erro=erro, lang=lang)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ═══════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════

@app.route('/dashboard')
@login_required
def dashboard():
    uid  = session['usuario_id']
    lang = get_lang()

    aves_ativas = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()

    total_aves    = len(aves_ativas)
    machos        = sum(1 for a in aves_ativas if a.sexo == 'Macho')
    femeas        = sum(1 for a in aves_ativas if a.sexo == 'Fêmea')
    total_ativas  = total_aves  # alias para % no template

    gaiolas       = Gaiola.query.filter_by(usuario_id=uid).count()

    posturas_all  = Postura.query.filter_by(usuario_id=uid).all()
    posturas_ativas = sum(1 for p in posturas_all if p.status != 'Encerrada')
    posturas_recentes = sorted(posturas_all, key=lambda p: p.id, reverse=True)[:5]

    filhotes_ativos = Filhote.query.filter_by(
        usuario_id=uid
    ).filter(
        Filhote.status.notin_(['Movido para plantel', 'Vendido', 'Falecido'])
    ).count()

    vendas_all  = Venda.query.filter_by(usuario_id=uid).all()
    aves_vendidas = len(vendas_all)
    receita_total = sum(v.valor or 0 for v in vendas_all)

    valor_plantel = sum(a.valor_venda or 0 for a in aves_ativas)

    # Distribuição por espécie
    especies = {}
    for a in aves_ativas:
        esp = a.especie or 'Não informada'
        especies[esp] = especies.get(esp, 0) + 1
    especies = dict(sorted(especies.items(), key=lambda x: x[1], reverse=True))

    return render_template('dashboard.html',
        lang             = lang,
        total_aves       = total_aves,
        machos           = machos,
        femeas           = femeas,
        total_ativas     = total_ativas,
        gaiolas          = gaiolas,
        posturas_ativas  = posturas_ativas,
        posturas_recentes= posturas_recentes,
        filhotes_ativos  = filhotes_ativos,
        aves_vendidas    = aves_vendidas,
        receita_total    = receita_total,
        valor_plantel    = valor_plantel,
        especies         = especies,
    )
# ═══════════════════════════════════════════
# PLANTEL
# ═══════════════════════════════════════════

@app.route('/plantel')
@login_required
def plantel():
    uid  = session['usuario_id']
    lang = get_lang()

    q      = request.args.get('q', '').strip()
    sexo   = request.args.get('sexo', '')
    status = request.args.get('status', '')

    query = Ave.query.filter_by(usuario_id=uid)

    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Ave.anilha.ilike(like),
                Ave.especie.ilike(like),
                Ave.genetica.ilike(like),
                Ave.subespecie.ilike(like),
            )
        )

    if sexo:
        query = query.filter_by(sexo=sexo)

    if status:
        query = query.filter_by(status=status)

    aves = query.order_by(Ave.id.desc()).all()

    return render_template('plantel.html',
        lang   = lang,
        aves   = aves,
        q      = q,
        sexo   = sexo,
        status = status,
    )


@app.route('/plantel/nova', methods=['GET', 'POST'])
@login_required
def nova_ave():
    uid  = session['usuario_id']
    lang = get_lang()
    gaiolas = Gaiola.query.filter_by(usuario_id=uid).all()
    erro = None

    if request.method == 'POST':
        anilha = request.form.get('anilha', '').strip()

        if not anilha:
            erros = {
                'pt': 'A anilha é obrigatória.',
                'en': 'The ring is required.',
                'fr': 'La bague est obligatoire.',
                'de': 'Der Ring ist erforderlich.',
            }
            erro = erros.get(lang)
        elif Ave.query.filter_by(usuario_id=uid, anilha=anilha).first():
            erros = {
                'pt': 'Já existe uma ave com esta anilha.',
                'en': 'A bird with this ring already exists.',
                'fr': 'Un oiseau avec cette bague existe déjà.',
                'de': 'Ein Vogel mit diesem Ring existiert bereits.',
            }
            erro = erros.get(lang)
        else:
            gaiola_id = parse_int(request.form.get('gaiola_id')) or None

            a = Ave(
                usuario_id            = uid,
                anilha                = anilha,
                cor_anilha            = request.form.get('cor_anilha', '#52b788'),
                especie               = request.form.get('especie', '').strip(),
                subespecie            = request.form.get('subespecie', '').strip(),
                sexo                  = request.form.get('sexo', 'Indeterminado'),
                cor_plumagem          = request.form.get('cor_plumagem', '').strip(),
                genetica              = request.form.get('genetica', '').strip(),
                data_nascimento       = parse_date(request.form.get('data_nascimento')),
                data_aquisicao        = parse_date(request.form.get('data_aquisicao')),
                custo_aquisicao       = parse_float(request.form.get('custo_aquisicao')),
                custo_alimentacao_mes = parse_float(request.form.get('custo_alimentacao_mes')),
                valor_venda           = parse_float(request.form.get('valor_venda')),
                status                = request.form.get('status', 'Ativo'),
                origem                = request.form.get('origem', 'Comprado'),
                observacoes           = request.form.get('observacoes', '').strip(),
                gaiola_id             = gaiola_id,
            )
            db.session.add(a)
            db.session.commit()
            return redirect(url_for('plantel'))

    titulo = {
        'pt': 'Nova Ave',
        'en': 'New Bird',
        'fr': 'Nouvel Oiseau',
        'de': 'Neuer Vogel',
    }.get(lang, 'Nova Ave')

    return render_template('form_ave.html',
        lang    = lang,
        ave     = None,
        gaiolas = gaiolas,
        erro    = erro,
        titulo  = titulo,
    )


@app.route('/plantel/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_ave(id):
    uid  = session['usuario_id']
    lang = get_lang()
    a    = Ave.query.filter_by(id=id, usuario_id=uid).first_or_404()
    gaiolas = Gaiola.query.filter_by(usuario_id=uid).all()
    erro = None

    if request.method == 'POST':
        anilha = request.form.get('anilha', '').strip()

        if not anilha:
            erros = {
                'pt': 'A anilha é obrigatória.',
                'en': 'The ring is required.',
                'fr': 'La bague est obligatoire.',
                'de': 'Der Ring ist erforderlich.',
            }
            erro = erros.get(lang)
        else:
            duplicada = Ave.query.filter(
                Ave.usuario_id == uid,
                Ave.anilha == anilha,
                Ave.id != id
            ).first()

            if duplicada:
                erros = {
                    'pt': 'Já existe outra ave com esta anilha.',
                    'en': 'Another bird with this ring already exists.',
                    'fr': 'Un autre oiseau avec cette bague existe déjà.',
                    'de': 'Ein anderer Vogel mit diesem Ring existiert bereits.',
                }
                erro = erros.get(lang)
            else:
                gaiola_id = parse_int(request.form.get('gaiola_id')) or None

                a.anilha                = anilha
                a.cor_anilha            = request.form.get('cor_anilha', '#52b788')
                a.especie               = request.form.get('especie', '').strip()
                a.subespecie            = request.form.get('subespecie', '').strip()
                a.sexo                  = request.form.get('sexo', 'Indeterminado')
                a.cor_plumagem          = request.form.get('cor_plumagem', '').strip()
                a.genetica              = request.form.get('genetica', '').strip()
                a.data_nascimento       = parse_date(request.form.get('data_nascimento'))
                a.data_aquisicao        = parse_date(request.form.get('data_aquisicao'))
                a.custo_aquisicao       = parse_float(request.form.get('custo_aquisicao'))
                a.custo_alimentacao_mes = parse_float(request.form.get('custo_alimentacao_mes'))
                a.valor_venda           = parse_float(request.form.get('valor_venda'))
                a.status                = request.form.get('status', 'Ativo')
                a.origem                = request.form.get('origem', 'Comprado')
                a.observacoes           = request.form.get('observacoes', '').strip()
                a.gaiola_id             = gaiola_id

                db.session.commit()
                return redirect(url_for('plantel'))

    titulo = {
        'pt': f'Editar Ave — {a.anilha}',
        'en': f'Edit Bird — {a.anilha}',
        'fr': f'Modifier Oiseau — {a.anilha}',
        'de': f'Vogel Bearbeiten — {a.anilha}',
    }.get(lang)

    return render_template('form_ave.html',
        lang    = lang,
        ave     = a,
        gaiolas = gaiolas,
        erro    = erro,
        titulo  = titulo,
    )


@app.route('/plantel/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_ave(id):
    uid = session['usuario_id']
    a   = Ave.query.filter_by(id=id, usuario_id=uid).first_or_404()
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('plantel'))


# ═══════════════════════════════════════════
# GAIOLAS
# ═══════════════════════════════════════════

@app.route('/gaiolas')
@login_required
def gaiolas():
    uid  = session['usuario_id']
    lang = get_lang()

    gaiolas_list   = Gaiola.query.filter_by(usuario_id=uid).all()
    aves_sem_gaiola = Ave.query.filter_by(
        usuario_id=uid,
        status='Ativo',
        gaiola_id=None
    ).all()

    return render_template('gaiolas.html',
        lang            = lang,
        gaiolas         = gaiolas_list,
        aves_sem_gaiola = aves_sem_gaiola,
    )


@app.route('/gaiolas/nova', methods=['POST'])
@login_required
def nova_gaiola():
    uid = session['usuario_id']

    g = Gaiola(
        usuario_id  = uid,
        nome        = request.form.get('nome', '').strip(),
        tipo        = request.form.get('tipo', 'Reprodução'),
        capacidade  = parse_int(request.form.get('capacidade'), 2),
        localizacao = request.form.get('localizacao', '').strip(),
        observacoes = request.form.get('observacoes', '').strip(),
    )
    db.session.add(g)
    db.session.commit()
    return redirect(url_for('gaiolas'))


@app.route('/gaiola/editar/<int:id>', methods=['POST'])
@login_required
def editar_gaiola(id):
    uid = session['usuario_id']
    g   = Gaiola.query.filter_by(id=id, usuario_id=uid).first_or_404()

    g.nome        = request.form.get('nome', '').strip()
    g.tipo        = request.form.get('tipo', 'Reprodução')
    g.capacidade  = parse_int(request.form.get('capacidade'), 2)
    g.localizacao = request.form.get('localizacao', '').strip()
    g.observacoes = request.form.get('observacoes', '').strip()

    db.session.commit()
    return redirect(url_for('gaiolas'))


@app.route('/gaiolas/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_gaiola(id):
    uid = session['usuario_id']
    g   = Gaiola.query.filter_by(id=id, usuario_id=uid).first_or_404()

    # Desvincula aves antes de deletar
    for a in g.aves:
        a.gaiola_id = None

    db.session.delete(g)
    db.session.commit()
    return redirect(url_for('gaiolas'))


@app.route('/gaiolas/mover-ave', methods=['POST'])
@login_required
def mover_ave_gaiola():
    uid       = session['usuario_id']
    ave_id    = parse_int(request.form.get('ave_id'))
    gaiola_id = parse_int(request.form.get('gaiola_id')) or None

    a = Ave.query.filter_by(id=ave_id, usuario_id=uid).first_or_404()
    a.gaiola_id = gaiola_id
    db.session.commit()
    return redirect(url_for('gaiolas'))
# ═══════════════════════════════════════════
# POSTURAS
# ═══════════════════════════════════════════

@app.route('/posturas')
@login_required
def posturas():
    uid  = session['usuario_id']
    lang = get_lang()

    posturas_list = Postura.query.filter_by(usuario_id=uid)\
                                 .order_by(Postura.id.desc()).all()

    femeas = Ave.query.filter_by(usuario_id=uid, sexo='Fêmea', status='Ativo').all()
    machos = Ave.query.filter_by(usuario_id=uid, sexo='Macho', status='Ativo').all()
    gaiolas_list = Gaiola.query.filter_by(usuario_id=uid).all()

    return render_template('posturas.html',
        lang     = lang,
        posturas = posturas_list,
        femeas   = femeas,
        machos   = machos,
        gaiolas  = gaiolas_list,
    )


@app.route('/posturas/nova', methods=['POST'])
@login_required
def nova_postura():
    uid  = session['usuario_id']

    femea_id   = parse_int(request.form.get('femea_id')) or None
    macho_id   = parse_int(request.form.get('macho_id')) or None
    gaiola_id  = parse_int(request.form.get('gaiola_id')) or None

    p = Postura(
        usuario_id      = uid,
        femea_id        = femea_id,
        macho_id        = macho_id,
        gaiola_id       = gaiola_id,
        data_postura    = parse_date(request.form.get('data_postura')),
        total_ovos      = parse_int(request.form.get('total_ovos')),
        ovos_fecundados = parse_int(request.form.get('ovos_fecundados')),
        ovos_eclodidos  = parse_int(request.form.get('ovos_eclodidos')),
        status          = request.form.get('status', 'Em andamento'),
        observacoes     = request.form.get('observacoes', '').strip(),
    )
    db.session.add(p)
    db.session.flush()  # gera p.id antes do commit

    # Cria filhotes automaticamente conforme ovos eclodidos
    _sincronizar_filhotes(p, uid)

    db.session.commit()
    return redirect(url_for('posturas'))


@app.route('/postura/editar/<int:id>', methods=['POST'])
@login_required
def editar_postura(id):
    uid = session['usuario_id']
    p   = Postura.query.filter_by(id=id, usuario_id=uid).first_or_404()

    p.femea_id        = parse_int(request.form.get('femea_id')) or None
    p.macho_id        = parse_int(request.form.get('macho_id')) or None
    p.gaiola_id       = parse_int(request.form.get('gaiola_id')) or None
    p.data_postura    = parse_date(request.form.get('data_postura'))
    p.total_ovos      = parse_int(request.form.get('total_ovos'))
    p.ovos_fecundados = parse_int(request.form.get('ovos_fecundados'))
    p.ovos_eclodidos  = parse_int(request.form.get('ovos_eclodidos'))
    p.status          = request.form.get('status', 'Em andamento')
    p.observacoes     = request.form.get('observacoes', '').strip()

    # Sincroniza filhotes com o novo número de eclodidos
    _sincronizar_filhotes(p, uid)

    db.session.commit()
    return redirect(url_for('posturas'))


@app.route('/postura/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_postura(id):
    uid = session['usuario_id']
    p   = Postura.query.filter_by(id=id, usuario_id=uid).first_or_404()

    # Remove filhotes vinculados
    for f in p.filhotes:
        db.session.delete(f)

    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('posturas'))


def _sincronizar_filhotes(postura, uid):
    """
    Garante que o número de filhotes no berçário bata com
    ovos_eclodidos. Cria novos ou remove os excedentes.
    """
    filhotes_atuais = postura.filhotes
    qtd_atual       = len(filhotes_atuais)
    qtd_alvo        = postura.ovos_eclodidos or 0

    # Herda espécie da fêmea se disponível
    especie = ''
    if postura.femea_id:
        femea = Ave.query.get(postura.femea_id)
        if femea:
            especie = femea.especie or ''

    if qtd_alvo > qtd_atual:
        for _ in range(qtd_alvo - qtd_atual):
            f = Filhote(
                usuario_id   = uid,
                postura_id   = postura.id,
                femea_id     = postura.femea_id,
                macho_id     = postura.macho_id,
                especie      = especie,
                data_eclosao = postura.data_postura,
                status       = 'No berçário',
            )
            db.session.add(f)

    elif qtd_alvo < qtd_atual:
        # Remove os mais recentes primeiro
        excedentes = sorted(filhotes_atuais, key=lambda f: f.id, reverse=True)
        for f in excedentes[:qtd_atual - qtd_alvo]:
            db.session.delete(f)


# ═══════════════════════════════════════════
# BERÇÁRIO
# ═══════════════════════════════════════════

@app.route('/bercario')
@login_required
def bercario():
    uid  = session['usuario_id']
    lang = get_lang()

    filhotes = Filhote.query.filter_by(usuario_id=uid)\
                            .order_by(Filhote.id.desc()).all()

    total      = len(filhotes)
    anilhados  = sum(1 for f in filhotes if f.anilha and f.anilha.strip())
    sem_anilha = total - anilhados

    return render_template('bercario.html',
        lang       = lang,
        filhotes   = filhotes,
        total      = total,
        anilhados  = anilhados,
        sem_anilha = sem_anilha,
    )


@app.route('/bercario/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_filhote(id):
    uid  = session['usuario_id']
    lang = get_lang()
    f    = Filhote.query.filter_by(id=id, usuario_id=uid).first_or_404()

    if request.method == 'POST':
        f.especie     = request.form.get('especie', '').strip()
        f.sexo        = request.form.get('sexo', 'Indeterminado')
        f.anilha      = request.form.get('anilha', '').strip()
        f.cor_anilha  = request.form.get('cor_anilha', '#52b788')
        f.genetica    = request.form.get('genetica', '').strip()
        f.valor_venda = parse_float(request.form.get('valor_venda'))
        f.observacoes = request.form.get('observacoes', '').strip()
        f.status      = request.form.get('status', 'No berçário')

        # Botão "Salvar e Mover para Plantel"
        if request.form.get('mover_plantel'):
            f.status = 'Movido para plantel'
            db.session.commit()
            return redirect(url_for('filhote_para_plantel', id=f.id))

        db.session.commit()
        return redirect(url_for('bercario'))

    return render_template('form_filhote.html',
        lang    = lang,
        filhote = f,
    )


@app.route('/bercario/para-plantel/<int:id>')
@login_required
def filhote_para_plantel(id):
    uid  = session['usuario_id']
    f    = Filhote.query.filter_by(id=id, usuario_id=uid).first_or_404()

    # Verifica se já foi movido
    if f.status == 'Movido para plantel' and f.anilha:
        existe = Ave.query.filter_by(usuario_id=uid, anilha=f.anilha).first()
        if not existe:
            a = Ave(
                usuario_id      = uid,
                anilha          = f.anilha,
                cor_anilha      = f.cor_anilha or '#52b788',
                especie         = f.especie or '',
                sexo            = f.sexo or 'Indeterminado',
                genetica        = f.genetica or '',
                valor_venda     = f.valor_venda or 0.0,
                data_nascimento = f.data_eclosao,
                status          = 'Ativo',
                origem          = 'Nascido no criadouro',
                observacoes     = f.observacoes or '',
            )
            db.session.add(a)

    f.status = 'Movido para plantel'
    db.session.commit()
    return redirect(url_for('bercario'))


@app.route('/bercario/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_filhote(id):
    uid = session['usuario_id']
    f   = Filhote.query.filter_by(id=id, usuario_id=uid).first_or_404()
    db.session.delete(f)
    db.session.commit()
    return redirect(url_for('bercario'))


# ═══════════════════════════════════════════
# VENDAS
# ═══════════════════════════════════════════

@app.route('/vendas')
@login_required
def vendas():
    uid  = session['usuario_id']
    lang = get_lang()

    vendas_list = Venda.query.filter_by(usuario_id=uid)\
                             .order_by(Venda.id.desc()).all()

    aves_ativas = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()

    receita    = sum(v.valor or 0 for v in vendas_list)
    custo_total = sum(v.ave.custo_total() if v.ave else 0 for v in vendas_list)
    lucro      = receita - custo_total

    return render_template('vendas.html',
        lang        = lang,
        vendas      = vendas_list,
        aves_ativas = aves_ativas,
        receita     = receita,
        custo_total = custo_total,
        lucro       = lucro,
    )


@app.route('/vendas/nova', methods=['POST'])
@login_required
def nova_venda():
    uid    = session['usuario_id']
    ave_id = parse_int(request.form.get('ave_id')) or None

    if ave_id:
        a = Ave.query.filter_by(id=ave_id, usuario_id=uid).first()
        if a:
            a.status = 'Vendido'

    v = Venda(
        usuario_id  = uid,
        ave_id      = ave_id,
        data_venda  = parse_date(request.form.get('data_venda')),
        valor       = parse_float(request.form.get('valor')),
        comprador   = request.form.get('comprador', '').strip(),
        contato     = request.form.get('contato', '').strip(),
        observacoes = request.form.get('observacoes', '').strip(),
    )
    db.session.add(v)
    db.session.commit()
    return redirect(url_for('vendas'))


@app.route('/vendas/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_venda(id):
    uid = session['usuario_id']
    v   = Venda.query.filter_by(id=id, usuario_id=uid).first_or_404()

    # Reverte status da ave para Ativo
    if v.ave:
        v.ave.status = 'Ativo'

    db.session.delete(v)
    db.session.commit()
    return redirect(url_for('vendas'))
# ═══════════════════════════════════════════
# PERFIL
# ═══════════════════════════════════════════

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    uid  = session['usuario_id']
    lang = get_lang()
    u    = Usuario.query.get(uid)
    msg  = None
    msg_type = 'success'

    if request.method == 'POST':
        acao = request.form.get('acao')

        # ── Dados pessoais ──────────────────────────
        if acao == 'dados':
            nome  = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()

            if not nome or not email:
                msg_type = 'danger'
                msg = {
                    'pt': 'Nome e e-mail são obrigatórios.',
                    'en': 'Name and email are required.',
                    'fr': 'Nom et e-mail sont obligatoires.',
                    'de': 'Name und E-Mail sind erforderlich.',
                }.get(lang)
            else:
                duplicado = Usuario.query.filter(
                    Usuario.email == email,
                    Usuario.id != uid
                ).first()

                if duplicado:
                    msg_type = 'danger'
                    msg = {
                        'pt': 'Este e-mail já está em uso.',
                        'en': 'This email is already in use.',
                        'fr': 'Cet e-mail est déjà utilisé.',
                        'de': 'Diese E-Mail wird bereits verwendet.',
                    }.get(lang)
                else:
                    u.nome      = nome
                    u.email     = email
                    u.criadouro = request.form.get('criadouro', '').strip()
                    u.telefone  = request.form.get('telefone', '').strip()
                    session['nome'] = u.nome
                    db.session.commit()
                    msg = {
                        'pt': 'Dados atualizados com sucesso.',
                        'en': 'Data updated successfully.',
                        'fr': 'Données mises à jour avec succès.',
                        'de': 'Daten erfolgreich aktualisiert.',
                    }.get(lang)

        # ── Senha ───────────────────────────────────
        elif acao == 'senha':
            senha_atual = request.form.get('senha_atual', '')
            senha_nova  = request.form.get('senha_nova', '')
            senha_nova2 = request.form.get('senha_nova2', '')

            if not u.check_senha(senha_atual):
                msg_type = 'danger'
                msg = {
                    'pt': 'Senha atual incorreta.',
                    'en': 'Current password is incorrect.',
                    'fr': 'Mot de passe actuel incorrect.',
                    'de': 'Aktuelles Passwort ist falsch.',
                }.get(lang)

            elif senha_nova != senha_nova2:
                msg_type = 'danger'
                msg = {
                    'pt': 'As novas senhas não coincidem.',
                    'en': 'New passwords do not match.',
                    'fr': 'Les nouveaux mots de passe ne correspondent pas.',
                    'de': 'Neue Passwörter stimmen nicht überein.',
                }.get(lang)

            elif len(senha_nova) < 6:
                msg_type = 'danger'
                msg = {
                    'pt': 'A nova senha deve ter pelo menos 6 caracteres.',
                    'en': 'New password must have at least 6 characters.',
                    'fr': 'Le nouveau mot de passe doit avoir au moins 6 caractères.',
                    'de': 'Neues Passwort muss mindestens 6 Zeichen haben.',
                }.get(lang)

            else:
                u.set_senha(senha_nova)
                db.session.commit()
                msg = {
                    'pt': 'Senha alterada com sucesso.',
                    'en': 'Password changed successfully.',
                    'fr': 'Mot de passe modifié avec succès.',
                    'de': 'Passwort erfolgreich geändert.',
                }.get(lang)

        # ── Idioma ──────────────────────────────────
        elif acao == 'idioma':
            novo_lang = request.form.get('lang', 'pt')
            if novo_lang in ('pt', 'en', 'fr', 'de'):
                u.lang = novo_lang
                session['lang'] = novo_lang
                lang = novo_lang
                db.session.commit()
                msg = {
                    'pt': 'Idioma atualizado com sucesso.',
                    'en': 'Language updated successfully.',
                    'fr': 'Langue mise à jour avec succès.',
                    'de': 'Sprache erfolgreich aktualisiert.',
                }.get(lang)

    return render_template('perfil.html',
        lang     = lang,
        usuario  = u,
        msg      = msg,
        msg_type = msg_type,
    )


# ... (seu código existente, incluindo os modelos e outras rotas) ...

# ═══════════════════════════════════════════
# CRUZAMENTOS
# ═══════════════════════════════════════════

@app.route('/cruzamentos')
@login_required
def cruzamentos():
    uid  = session['usuario_id']
    lang = get_lang()

    machos  = Ave.query.filter_by(usuario_id=uid, sexo='Macho', status='Ativo').all()
    femeas  = Ave.query.filter_by(usuario_id=uid, sexo='Fêmea', status='Ativo').all()
    todas   = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()

    especies = sorted(list(set(a.especie for a in todas if a.especie)))

    return render_template('cruzamentos.html',
        lang     = lang,
        machos   = machos,
        femeas   = femeas,
        especies = especies,
    )


# ═══════════════════════════════════════════
# CALCULADORA DE DIETA
# ═══════════════════════════════════════════

@app.route('/calculadora')
@login_required
def calculadora():
    uid  = session['usuario_id']
    lang = get_lang()

    aves    = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()
    todas   = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()

    especies = sorted(list(set(a.especie for a in todas if a.especie)))

    return render_template('calculadora_alimentacao.html',
        lang     = lang,
        aves     = aves,
        especies = especies,
    )


# ═══════════════════════════════════════════
# PLANOS DE ASSINATURA
# ═══════════════════════════════════════════

@app.route('/planos') # Esta rota agora é para os Planos de Assinatura
@login_required
def planos():
    lang = get_lang()
    # Aqui você pode passar informações sobre os planos de assinatura, se houver
    return render_template('planos.html', # Este é o template para Planos de Assinatura
        lang = lang,
    )

# ═══════════════════════════════════════════
# INICIALIZAÇÃO DO APP (deve ser a última coisa no arquivo)
# ═══════════════════════════════════════════

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)