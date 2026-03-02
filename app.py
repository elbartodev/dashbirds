from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = 'dashbirds_secret_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashbirds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========================
# MODELS
# ========================

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    criadouro = db.Column(db.String(100), default='Criadouro Campestre')
    documento = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Ave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    anilha = db.Column(db.String(50), nullable=False)
    cor_anilha = db.Column(db.String(10), default='#52b788')
    especie = db.Column(db.String(100))
    subespecie = db.Column(db.String(100))
    sexo = db.Column(db.String(20), default='Indeterminado')
    cor_plumagem = db.Column(db.String(100))
    genetica = db.Column(db.String(200))
    data_nascimento = db.Column(db.Date)
    data_aquisicao = db.Column(db.Date)
    custo_aquisicao = db.Column(db.Float, default=0)
    valor_venda = db.Column(db.Float, default=0)
    custo_alimentacao_mes = db.Column(db.Float, default=0)
    gaiola_id = db.Column(db.Integer, db.ForeignKey('gaiola.id'), nullable=True)
    status = db.Column(db.String(20), default='Ativo')
    origem = db.Column(db.String(50), default='Comprado')
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    gaiola = db.relationship('Gaiola', backref='aves', foreign_keys=[gaiola_id])
    custos_variados = db.relationship('CustoVariado', backref='ave', cascade='all, delete-orphan')

    def custo_total(self):
        ref = self.data_nascimento or self.data_aquisicao
        meses = 0
        if ref:
            delta = date.today() - ref
            meses = max(0, delta.days // 30)
        alim = (self.custo_alimentacao_mes or 0) * meses
        var = sum(c.valor for c in self.custos_variados)
        return (self.custo_aquisicao or 0) + alim + var

    def idade_meses(self):
        ref = self.data_nascimento or self.data_aquisicao
        if not ref:
            return 0
        return max(0, (date.today() - ref).days // 30)


class Gaiola(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), default='Alojamento')
    capacidade = db.Column(db.Integer, default=2)
    localizacao = db.Column(db.String(100))
    observacoes = db.Column(db.Text)


class Postura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    femea_id = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    macho_id = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    gaiola_id = db.Column(db.Integer, db.ForeignKey('gaiola.id'), nullable=True)
    data_postura = db.Column(db.Date)
    total_ovos = db.Column(db.Integer, default=0)
    ovos_fecundados = db.Column(db.Integer, default=0)
    ovos_eclodidos = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='Em andamento')
    observacoes = db.Column(db.Text)
    femea = db.relationship('Ave', foreign_keys=[femea_id])
    macho = db.relationship('Ave', foreign_keys=[macho_id])
    gaiola = db.relationship('Gaiola', foreign_keys=[gaiola_id])


class Filhote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    postura_id = db.Column(db.Integer, db.ForeignKey('postura.id'), nullable=True)
    femea_id = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    macho_id = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    data_eclosao = db.Column(db.Date)
    especie = db.Column(db.String(100))
    sexo = db.Column(db.String(20), default='Indeterminado')
    anilha = db.Column(db.String(50))
    cor_anilha = db.Column(db.String(10), default='#52b788')
    genetica = db.Column(db.String(200))
    valor_venda = db.Column(db.Float, default=0)
    status = db.Column(db.String(30), default='No berçário')
    observacoes = db.Column(db.Text)
    postura = db.relationship('Postura', backref='filhotes')
    femea = db.relationship('Ave', foreign_keys=[femea_id])
    macho = db.relationship('Ave', foreign_keys=[macho_id])


class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ave_id = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    data_venda = db.Column(db.Date)
    valor = db.Column(db.Float, default=0)
    comprador = db.Column(db.String(100))
    contato = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    ave = db.relationship('Ave', backref='venda')
    custos_variados = db.relationship('CustoVariado', backref='venda', cascade='all, delete-orphan',
                                      primaryjoin='Venda.id == CustoVariado.venda_id')


class CustoVariado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ave_id = db.Column(db.Integer, db.ForeignKey('ave.id'), nullable=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('venda.id'), nullable=True)
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Float, default=0)


# ========================
# AUTH ROUTES
# ========================

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        user = Usuario.query.filter_by(email=email).first()
        if user and user.check_senha(senha):
            session['user_id'] = user.id
            session['user_nome'] = user.nome
            session['criadouro'] = user.criadouro
            return redirect(url_for('dashboard'))
        erro = 'E-mail ou senha incorretos.'
    return render_template('login.html', erro=erro)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    erro = None
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        criadouro = request.form.get('criadouro', '').strip() or 'Criadouro Campestre'
        documento = request.form.get('documento', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        senha2 = request.form.get('senha2', '')
        if not nome or not email or not senha:
            erro = 'Preencha todos os campos obrigatórios.'
        elif senha != senha2:
            erro = 'As senhas não coincidem.'
        elif len(senha) < 6:
            erro = 'A senha deve ter pelo menos 6 caracteres.'
        elif Usuario.query.filter_by(email=email).first():
            erro = 'Este e-mail já está cadastrado.'
        else:
            u = Usuario(nome=nome, criadouro=criadouro, documento=documento,
                        telefone=telefone, email=email)
            u.set_senha(senha)
            db.session.add(u)
            db.session.commit()
            session['user_id'] = u.id
            session['user_nome'] = u.nome
            session['criadouro'] = u.criadouro
            return redirect(url_for('dashboard'))
    return render_template('cadastro.html', erro=erro)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ========================
# MAIN PAGES
# ========================

@app.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    aves_ativas = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()
    aves_vendidas = Ave.query.filter_by(usuario_id=uid, status='Vendido').count()
    posturas_ativas = Postura.query.filter_by(usuario_id=uid).filter(Postura.status != 'Encerrada').count()
    filhotes_ativos = Filhote.query.filter_by(usuario_id=uid).filter(
        Filhote.status.in_(['No berçário', 'Desmamado'])).count()
    gaiolas = Gaiola.query.filter_by(usuario_id=uid).count()
    vendas = Venda.query.filter_by(usuario_id=uid).all()
    receita_total = sum(v.valor or 0 for v in vendas)
    machos = sum(1 for a in aves_ativas if a.sexo == 'Macho')
    femeas = sum(1 for a in aves_ativas if a.sexo == 'Fêmea')
    valor_plantel = sum((a.valor_venda or 0) if (a.valor_venda or 0) > 0 else a.custo_total() for a in aves_ativas)
    posturas_recentes = Postura.query.filter_by(usuario_id=uid).order_by(Postura.data_postura.desc()).limit(5).all()
    especies = {}
    for a in aves_ativas:
        k = a.especie or 'N/A'
        especies[k] = especies.get(k, 0) + 1
    return render_template('dashboard.html',
        total_aves=len(aves_ativas), aves_vendidas=aves_vendidas,
        posturas_ativas=posturas_ativas, filhotes_ativos=filhotes_ativos,
        gaiolas=gaiolas, receita_total=receita_total, machos=machos,
        femeas=femeas, valor_plantel=valor_plantel,
        posturas_recentes=posturas_recentes, especies=especies,
        total_ativas=len(aves_ativas) or 1)


@app.route('/plantel')
@login_required
def plantel():
    uid = session['user_id']
    q = request.args.get('q', '')
    sexo = request.args.get('sexo', '')
    status = request.args.get('status', '')
    query = Ave.query.filter_by(usuario_id=uid)
    if q:
        query = query.filter(
            db.or_(Ave.anilha.ilike(f'%{q}%'), Ave.especie.ilike(f'%{q}%'),
                   Ave.genetica.ilike(f'%{q}%'), Ave.subespecie.ilike(f'%{q}%')))
    if sexo:
        query = query.filter_by(sexo=sexo)
    if status:
        query = query.filter_by(status=status)
    aves = query.all()
    gaiolas = Gaiola.query.filter_by(usuario_id=uid).all()
    return render_template('plantel.html', aves=aves, gaiolas=gaiolas, q=q, sexo=sexo, status=status)


@app.route('/ave/nova', methods=['GET', 'POST'])
@login_required
def nova_ave():
    uid = session['user_id']
    gaiolas = Gaiola.query.filter_by(usuario_id=uid).all()
    erro = None
    if request.method == 'POST':
        anilha = request.form.get('anilha', '').strip()
        especie = request.form.get('especie', '').strip()
        if not anilha or not especie:
            erro = 'Anilha e espécie são obrigatórios.'
        else:
            nasc = request.form.get('data_nascimento') or None
            aq = request.form.get('data_aquisicao') or None
            gaiola_id = request.form.get('gaiola_id') or None
            a = Ave(
                usuario_id=uid, anilha=anilha,
                cor_anilha=request.form.get('cor_anilha', '#52b788'),
                especie=especie,
                subespecie=request.form.get('subespecie'),
                sexo=request.form.get('sexo', 'Indeterminado'),
                cor_plumagem=request.form.get('cor_plumagem'),
                genetica=request.form.get('genetica'),
                data_nascimento=datetime.strptime(nasc, '%Y-%m-%d').date() if nasc else None,
                data_aquisicao=datetime.strptime(aq, '%Y-%m-%d').date() if aq else None,
                custo_aquisicao=float(request.form.get('custo_aquisicao') or 0),
                valor_venda=float(request.form.get('valor_venda') or 0),
                custo_alimentacao_mes=float(request.form.get('custo_alimentacao_mes') or 0),
                gaiola_id=int(gaiola_id) if gaiola_id else None,
                status=request.form.get('status', 'Ativo'),
                origem=request.form.get('origem', 'Comprado'),
                observacoes=request.form.get('observacoes')
            )
            db.session.add(a)
            db.session.commit()
            if a.status == 'Vendido':
                v = Venda(usuario_id=uid, ave_id=a.id,
                          data_venda=date.today(),
                          valor=a.valor_venda or 0)
                db.session.add(v)
                db.session.commit()
            return redirect(url_for('plantel'))
    return render_template('form_ave.html', ave=None, gaiolas=gaiolas, erro=erro, titulo='Nova Ave')


@app.route('/ave/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_ave(id):
    uid = session['user_id']
    a = Ave.query.filter_by(id=id, usuario_id=uid).first_or_404()
    gaiolas = Gaiola.query.filter_by(usuario_id=uid).all()
    erro = None
    if request.method == 'POST':
        anilha = request.form.get('anilha', '').strip()
        especie = request.form.get('especie', '').strip()
        if not anilha or not especie:
            erro = 'Anilha e espécie são obrigatórios.'
        else:
            status_antigo = a.status
            nasc = request.form.get('data_nascimento') or None
            aq = request.form.get('data_aquisicao') or None
            gaiola_id = request.form.get('gaiola_id') or None
            a.anilha = anilha
            a.cor_anilha = request.form.get('cor_anilha', '#52b788')
            a.especie = especie
            a.subespecie = request.form.get('subespecie')
            a.sexo = request.form.get('sexo', 'Indeterminado')
            a.cor_plumagem = request.form.get('cor_plumagem')
            a.genetica = request.form.get('genetica')
            a.data_nascimento = datetime.strptime(nasc, '%Y-%m-%d').date() if nasc else None
            a.data_aquisicao = datetime.strptime(aq, '%Y-%m-%d').date() if aq else None
            a.custo_aquisicao = float(request.form.get('custo_aquisicao') or 0)
            a.valor_venda = float(request.form.get('valor_venda') or 0)
            a.custo_alimentacao_mes = float(request.form.get('custo_alimentacao_mes') or 0)
            a.gaiola_id = int(gaiola_id) if gaiola_id else None
            a.status = request.form.get('status', 'Ativo')
            a.origem = request.form.get('origem', 'Comprado')
            a.observacoes = request.form.get('observacoes')
            db.session.commit()
            if a.status == 'Vendido' and status_antigo != 'Vendido':
                if not Venda.query.filter_by(ave_id=a.id).first():
                    v = Venda(usuario_id=uid, ave_id=a.id,
                              data_venda=date.today(),
                              valor=a.valor_venda or 0)
                    db.session.add(v)
                    db.session.commit()
            return redirect(url_for('plantel'))
    return render_template('form_ave.html', ave=a, gaiolas=gaiolas, erro=erro, titulo='Editar Ave')


@app.route('/ave/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_ave(id):
    uid = session['user_id']
    a = Ave.query.filter_by(id=id, usuario_id=uid).first_or_404()
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('plantel'))


# ========================
# GAIOLAS
# ========================

@app.route('/gaiolas')
@login_required
def gaiolas():
    uid = session['user_id']
    gs = Gaiola.query.filter_by(usuario_id=uid).all()
    aves_sem_gaiola = Ave.query.filter_by(usuario_id=uid, status='Ativo').filter(Ave.gaiola_id == None).all()
    return render_template('gaiolas.html', gaiolas=gs, aves_sem_gaiola=aves_sem_gaiola)


@app.route('/gaiola/nova', methods=['POST'])
@login_required
def nova_gaiola():
    uid = session['user_id']
    cap = request.form.get('capacidade') or None
    g = Gaiola(
        usuario_id=uid,
        nome=request.form.get('nome', '').strip(),
        tipo=request.form.get('tipo', 'Alojamento'),
        capacidade=int(cap) if cap else 2,
        localizacao=request.form.get('localizacao'),
        observacoes=request.form.get('observacoes')
    )
    db.session.add(g)
    db.session.commit()
    return redirect(url_for('gaiolas'))


@app.route('/gaiola/editar/<int:id>', methods=['POST'])
@login_required
def editar_gaiola(id):
    uid = session['user_id']
    g = Gaiola.query.filter_by(id=id, usuario_id=uid).first_or_404()
    cap = request.form.get('capacidade') or None
    g.nome = request.form.get('nome', g.nome)
    g.tipo = request.form.get('tipo', g.tipo)
    g.capacidade = int(cap) if cap else g.capacidade
    g.localizacao = request.form.get('localizacao', g.localizacao)
    g.observacoes = request.form.get('observacoes', g.observacoes)
    db.session.commit()
    return redirect(url_for('gaiolas'))


@app.route('/gaiola/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_gaiola(id):
    uid = session['user_id']
    g = Gaiola.query.filter_by(id=id, usuario_id=uid).first_or_404()
    for a in g.aves:
        a.gaiola_id = None
    db.session.delete(g)
    db.session.commit()
    return redirect(url_for('gaiolas'))


@app.route('/gaiola/mover_ave', methods=['POST'])
@login_required
def mover_ave_gaiola():
    uid = session['user_id']
    ave_id = request.form.get('ave_id')
    gaiola_id = request.form.get('gaiola_id') or None
    a = Ave.query.filter_by(id=ave_id, usuario_id=uid).first_or_404()
    a.gaiola_id = int(gaiola_id) if gaiola_id else None
    db.session.commit()
    return redirect(url_for('gaiolas'))


# ========================
# POSTURAS
# ========================

@app.route('/posturas')
@login_required
def posturas():
    uid = session['user_id']
    ps = Postura.query.filter_by(usuario_id=uid).order_by(Postura.data_postura.desc()).all()
    femeas = Ave.query.filter_by(usuario_id=uid, sexo='Fêmea', status='Ativo').all()
    machos = Ave.query.filter_by(usuario_id=uid, sexo='Macho', status='Ativo').all()
    if not femeas:
        femeas = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()
    if not machos:
        machos = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()
    gaiolas = Gaiola.query.filter_by(usuario_id=uid).all()
    return render_template('posturas.html', posturas=ps, femeas=femeas, machos=machos, gaiolas=gaiolas)


@app.route('/postura/nova', methods=['POST'])
@login_required
def nova_postura():
    uid = session['user_id']
    data = request.form.get('data_postura') or None
    femea_id = request.form.get('femea_id') or None
    macho_id = request.form.get('macho_id') or None
    gaiola_id = request.form.get('gaiola_id') or None
    ovos_ecl = int(request.form.get('ovos_eclodidos') or 0)
    p = Postura(
        usuario_id=uid,
        femea_id=int(femea_id) if femea_id else None,
        macho_id=int(macho_id) if macho_id else None,
        gaiola_id=int(gaiola_id) if gaiola_id else None,
        data_postura=datetime.strptime(data, '%Y-%m-%d').date() if data else None,
        total_ovos=int(request.form.get('total_ovos') or 0),
        ovos_fecundados=int(request.form.get('ovos_fecundados') or 0),
        ovos_eclodidos=ovos_ecl,
        status=request.form.get('status', 'Em andamento'),
        observacoes=request.form.get('observacoes')
    )
    db.session.add(p)
    db.session.commit()
    if ovos_ecl > 0:
        gerar_filhotes(p, ovos_ecl, uid)
    return redirect(url_for('posturas'))


@app.route('/postura/editar/<int:id>', methods=['POST'])
@login_required
def editar_postura(id):
    uid = session['user_id']
    p = Postura.query.filter_by(id=id, usuario_id=uid).first_or_404()
    ecl_antigo = p.ovos_eclodidos or 0
    data = request.form.get('data_postura') or None
    femea_id = request.form.get('femea_id') or None
    macho_id = request.form.get('macho_id') or None
    gaiola_id = request.form.get('gaiola_id') or None
    novos_ecl = int(request.form.get('ovos_eclodidos') or 0)
    p.femea_id = int(femea_id) if femea_id else None
    p.macho_id = int(macho_id) if macho_id else None
    p.gaiola_id = int(gaiola_id) if gaiola_id else None
    p.data_postura = datetime.strptime(data, '%Y-%m-%d').date() if data else None
    p.total_ovos = int(request.form.get('total_ovos') or 0)
    p.ovos_fecundados = int(request.form.get('ovos_fecundados') or 0)
    p.ovos_eclodidos = novos_ecl
    p.status = request.form.get('status', p.status)
    p.observacoes = request.form.get('observacoes')
    db.session.commit()
    if novos_ecl > ecl_antigo:
        gerar_filhotes(p, novos_ecl - ecl_antigo, uid)
    return redirect(url_for('posturas'))


@app.route('/postura/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_postura(id):
    uid = session['user_id']
    p = Postura.query.filter_by(id=id, usuario_id=uid).first_or_404()
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('posturas'))


def gerar_filhotes(postura, quantidade, uid):
    femea = Ave.query.get(postura.femea_id) if postura.femea_id else None
    macho = Ave.query.get(postura.macho_id) if postura.macho_id else None
    esp = femea.especie if femea else (macho.especie if macho else '')
    for _ in range(quantidade):
        f = Filhote(
            usuario_id=uid,
            postura_id=postura.id,
            femea_id=postura.femea_id,
            macho_id=postura.macho_id,
            data_eclosao=date.today(),
            especie=esp,
            status='No berçário'
        )
        db.session.add(f)
    db.session.commit()


# ========================
# BERÇÁRIO
# ========================

@app.route('/bercario')
@login_required
def bercario():
    uid = session['user_id']
    filhotes = Filhote.query.filter_by(usuario_id=uid).order_by(Filhote.data_eclosao.desc()).all()
    total = len(filhotes)
    anilhados = sum(1 for f in filhotes if f.anilha)
    sem_anilha = sum(1 for f in filhotes if not f.anilha and f.status in ['No berçário', 'Desmamado'])
    return render_template('bercario.html', filhotes=filhotes, total=total,
                           anilhados=anilhados, sem_anilha=sem_anilha)


@app.route('/filhote/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_filhote(id):
    uid = session['user_id']
    f = Filhote.query.filter_by(id=id, usuario_id=uid).first_or_404()
    if request.method == 'POST':
        f.especie = request.form.get('especie', f.especie)
        f.sexo = request.form.get('sexo', f.sexo)
        f.anilha = request.form.get('anilha', '').strip() or None
        f.cor_anilha = request.form.get('cor_anilha', '#52b788')
        f.genetica = request.form.get('genetica')
        f.valor_venda = float(request.form.get('valor_venda') or 0)
        f.status = request.form.get('status', f.status)
        f.observacoes = request.form.get('observacoes')
        db.session.commit()
        if request.form.get('mover_plantel'):
            return redirect(url_for('filhote_para_plantel', id=f.id))
        return redirect(url_for('bercario'))
    gaiolas = Gaiola.query.filter_by(usuario_id=uid).all()
    return render_template('form_filhote.html', filhote=f, gaiolas=gaiolas)


@app.route('/filhote/plantel/<int:id>')
@login_required
def filhote_para_plantel(id):
    uid = session['user_id']
    f = Filhote.query.filter_by(id=id, usuario_id=uid).first_or_404()
    a = Ave(
        usuario_id=uid,
        anilha=f.anilha or f'F-{f.id}',
        cor_anilha=f.cor_anilha or '#52b788',
        especie=f.especie or '',
        sexo=f.sexo or 'Indeterminado',
        genetica=f.genetica,
        valor_venda=f.valor_venda or 0,
        data_nascimento=f.data_eclosao,
        status='Ativo',
        origem='Nascido no criadouro',
        observacoes=f'Movido do berçário. Postura #{f.postura_id}'
    )
    db.session.add(a)
    f.status = 'Movido para plantel'
    db.session.commit()
    return redirect(url_for('plantel'))


@app.route('/filhote/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_filhote(id):
    uid = session['user_id']
    f = Filhote.query.filter_by(id=id, usuario_id=uid).first_or_404()
    db.session.delete(f)
    db.session.commit()
    return redirect(url_for('bercario'))


# ========================
# VENDAS
# ========================

@app.route('/vendas')
@login_required
def vendas():
    uid = session['user_id']
    vs = Venda.query.filter_by(usuario_id=uid).order_by(Venda.data_venda.desc()).all()
    aves_ativas = Ave.query.filter_by(usuario_id=uid, status='Ativo').all()
    receita = sum(v.valor or 0 for v in vs)
    custo_total = sum(v.ave.custo_total() if v.ave else 0 for v in vs)
    lucro = receita - custo_total
    return render_template('vendas.html', vendas=vs, aves_ativas=aves_ativas,
                           receita=receita, custo_total=custo_total, lucro=lucro)


@app.route('/venda/nova', methods=['POST'])
@login_required
def nova_venda():
    uid = session['user_id']
    ave_id = request.form.get('ave_id') or None
    data = request.form.get('data_venda') or None
    v = Venda(
        usuario_id=uid,
        ave_id=int(ave_id) if ave_id else None,
        data_venda=datetime.strptime(data, '%Y-%m-%d').date() if data else date.today(),
        valor=float(request.form.get('valor') or 0),
        comprador=request.form.get('comprador'),
        contato=request.form.get('contato'),
        observacoes=request.form.get('observacoes')
    )
    db.session.add(v)
    if ave_id:
        a = Ave.query.get(int(ave_id))
        if a:
            a.status = 'Vendido'
            if not a.valor_venda:
                a.valor_venda = v.valor
    db.session.commit()
    return redirect(url_for('vendas'))


@app.route('/venda/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_venda(id):
    uid = session['user_id']
    v = Venda.query.filter_by(id=id, usuario_id=uid).first_or_404()
    if v.ave:
        v.ave.status = 'Ativo'
    db.session.delete(v)
    db.session.commit()
    return redirect(url_for('vendas'))


@app.route('/custo/add', methods=['POST'])
@login_required
def add_custo():
    uid = session['user_id']
    ave_id = request.form.get('ave_id') or None
    venda_id = request.form.get('venda_id') or None
    c = CustoVariado(
        ave_id=int(ave_id) if ave_id else None,
        venda_id=int(venda_id) if venda_id else None,
        descricao=request.form.get('descricao'),
        valor=float(request.form.get('valor') or 0)
    )
    db.session.add(c)
    if ave_id:
        a = Ave.query.get(int(ave_id))
        if a:
            a.custosVar = a.custos_variados
    db.session.commit()
    return redirect(request.referrer or url_for('vendas'))


@app.route('/custo/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_custo(id):
    c = CustoVariado.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return redirect(request.referrer or url_for('vendas'))


# ========================
# PERFIL
# ========================

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    uid = session['user_id']
    u = Usuario.query.get(uid)
    msg = None
    msg_type = 'success'
    if request.method == 'POST':
        acao = request.form.get('acao')
        if acao == 'dados':
            u.nome = request.form.get('nome', u.nome).strip()
            u.criadouro = request.form.get('criadouro', u.criadouro).strip()
            u.email = request.form.get('email', u.email).strip()
            u.telefone = request.form.get('telefone', u.telefone)
            db.session.commit()
            session['user_nome'] = u.nome
            session['criadouro'] = u.criadouro
            msg = 'Dados atualizados com sucesso!'
        elif acao == 'senha':
            atual = request.form.get('senha_atual')
            nova = request.form.get('senha_nova')
            nova2 = request.form.get('senha_nova2')
            if not u.check_senha(atual):
                msg = 'Senha atual incorreta.'
                msg_type = 'danger'
            elif nova != nova2:
                msg = 'As novas senhas não coincidem.'
                msg_type = 'danger'
            elif len(nova) < 6:
                msg = 'A nova senha deve ter pelo menos 6 caracteres.'
                msg_type = 'danger'
            else:
                u.set_senha(nova)
                db.session.commit()
                msg = 'Senha alterada com sucesso!'
    return render_template('perfil.html', usuario=u, msg=msg, msg_type=msg_type)


# ========================
# RUN
# ========================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)