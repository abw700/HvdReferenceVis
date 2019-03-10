from app import db


# Article object
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    abstract = db.Column(db.Text)
    pubyear = db.Column(db.Integer)
    jid = db.Column(db.Integer)

    def __repr__(self):
        return '<Article %r>' % (self.title)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # get article by id
    def get(self, id):
        return self.query.filter_by(id=id).limit(1).all()


# Journal object
class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __repr__(self):
        return '<Journal %r>' % (self.name)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # get journal by id
    def get(self, id):
        return self.query.filter_by(id=id).limit(1).all()

    # get all journal
    def get_all(self):
        return self.query.all()


# Citation object
class Citation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    apmid = db.Column(db.Integer)
    bpmid = db.Column(db.Integer)

    def __repr__(self):
        return '<Citation %r>' % (self.id)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # get articles that cite pmid
    def get_incoming(self, id):
        result = self.query.with_entities(Citation.apmid).filter_by(bpmid=id).all()
        n = len(result)
        return {'count': n, 'citing_pmid': [{'id': r[0]} for r in result]}

    # get articles that pmid cites
    def get_outgoing(self, id):
        result = self.query.with_entities(Citation.bpmid).filter_by(apmid=id).all()
        n = len(result)
        return {'count': n, 'cited_pmid': [{'id': r[0]} for r in result]}


