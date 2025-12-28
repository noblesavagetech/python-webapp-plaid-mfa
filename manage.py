from app import create_app, db

app = create_app()


@app.shell_context_processor
def make_shell_context():
    from app.models import User, QuestionnaireResponse, WaveToken
    return dict(db=db, User=User, QuestionnaireResponse=QuestionnaireResponse, WaveToken=WaveToken)
