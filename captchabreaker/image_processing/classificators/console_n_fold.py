from captchabreaker import app
from captchabreaker.image_processing.classificators.verificator import Verificator

# Change ID according to real model in DB
CLASSIFICATOR_ID = 39

app.app_context().push()

verificator = Verificator(CLASSIFICATOR_ID, print_progress=True)
result = verificator.perform()

print(result)
