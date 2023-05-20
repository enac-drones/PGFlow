# ENV defaults to local (so that requirements/local.txt are installed), but can be overridden
#  (e.g. ENV=production make setup).
ENV ?= local
# PYTHON specifies the python binary to use when creating virtualenv
PYTHON ?= python3.9

# Editor can be defined globally but defaults to nano
EDITOR ?= nano

# By default we open the editor after copying settings, but can be overridden
#  (e.g. EDIT_SETTINGS=no make settings).
EDIT_SETTINGS ?= yes

# Get root dir and project dir
PROJECT_ROOT ?= $(PWD)
SITE_ROOT 	 ?= $(PROJECT_ROOT)

BLACK	?= \033[0;30m
RED		?= \033[0;31m
GREEN	?= \033[0;32m
LIGHT_GREEN ?= \033[1;32m
YELLOW	?= \033[0;33m
BLUE	?= \033[0;34m
LIGHT_BLUE ?= \033[1;36m
PURPLE	?= \033[0;35m
CYAN	?= \033[0;36m
GRAY	?= \033[0;37m
COFF	?= \033[0m

INFO 	?= $(LIGHT_BLUE)
SUCCESS ?= $(LIGHT_GREEN)
WARNING ?= $(YELLOW)
ERROR 	?= $(RED)
DEBUG 	?= $(CYAN)
FORMAT 	?= $(GRAY)
BOLD ?= \033[1m


DOCKER_COMPOSE			= docker-compose
DOCKER_COMPOSE_RUN		= $(DOCKER_COMPOSE) run --rm
DOCKER_COMPOSE_DJANGO	= $(DOCKER_COMPOSE_RUN) django

.PHONY: all help validate-system-packages  setup run
.PHONY: clean pre-commit test psql
.PHONY: migrate docker-logs makemessages compilemessages psql


all: help


help:
	@echo "+------<<<<                                 Configuration                                >>>>------+"
	@echo ""
	@echo "ENV: $(ENV)"
	@echo "PYTHON: $(PYTHON)"
	@echo "PROJECT_ROOT: $(PROJECT_ROOT)"
	@echo "SITE_ROOT: $(SITE_ROOT)"
	@echo ""
	@echo "+------<<<<                                     Tasks                                    >>>>------+"
	@echo ""
	@echo "$(CYAN)make setup$(COFF)    - Sets up the project in your local machine"
	@echo "                This includes copying PyCharm files, creating local settings file, and setting up Docker."
	@echo ""
	@echo "$(CYAN)make pycharm$(COFF)  - Copies default PyCharm settings (unless they already exist)"
	@echo ""
	@echo "$(CYAN)make test$(COFF)     - Runs automatic tests on your python code"
	@echo ""
	@echo "$(CYAN)make pre-commit$(COFF)  - Runs automatic code quality tests on your code"
	@echo ""

validate-system-packages:
	@echo "$(INFO)Validating system packages...$(COFF)"
	@which poetry > /dev/null                      || (echo "$(ERROR)Poetry not found. Please install it. (make setup_env)$(COFF)" && exit 1)
	@#which rabbitmqctl > /dev/null         || (echo "$(ERROR)RabbitMQ command line tool not found. Please install it.$(COFF)" && exit 1)
	@#which docker > /dev/null                       || (echo "$(ERROR)Docker not found. Please install it.$(COFF)" && exit 1)
	@#which docker-compose > /dev/null       || (echo "$(ERROR)Docker Compose not found. Please install it.$(COFF)" && exit 1)
	@echo "All required system packages are installed."

.env:
	@echo "$(CYAN)Creating .env file$(COFF)"
	@cp .env-dev-example .env

dir_setup: .env

setup_poetry:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install
setup:
	@echo "$(CYAN)Setting up environment$(COFF)"
	make setup_poetry
	make dir_setup
	@echo "$(SUCCESS)Setup Complete$(COFF)"

test: validate-system-packages
	@echo "$(CYAN)Running Tests$(COFF)"
	poetry run pytest

pre-commit:
	@echo "$(CYAN)Running pre-commit$(COFF)"
	poetry run pre-commit run --all-files

run:
	poetry run python3 examples/simple_sim.py