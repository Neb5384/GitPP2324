#-*- coding: utf-8 -*-
from flask import Flask, jsonify
import RPi.GPIO as GPIO
import time

# Initialisation de l'application Flask
app = Flask(__name__)

# Configuration des broches GPIO selon la numérotation BCM
GPIO.setmode(GPIO.BCM)

# Définition d'un dictionnaire pour mapper les positions aux numéros des broches
led_matrix = {
    "Position1": {"red": 17, "green": 27, "blue": 22, "white": 4},
    "Position2": {"red": 18, "green": 23, "blue": 24, "white": 25},
    "Position3": {"red": 5, "green": 6, "blue": 12, "white": 13},
    "Position4": {"red": 19, "green": 16, "blue": 26, "white": 20},
    "Position5": {"red": 21, "green": 20, "blue": 7, "white": 8},
}

# Ensemble de positions valides
valid_positions = {"Position1", "Position2", "Position3", "Position4", "Position5"}

def setup_and_activate(position, color, state):
    """Configurer la broche GPIO pour une couleur et un état spécifiques."""
    pin_number = led_matrix[position][color]
    GPIO.setup(pin_number, GPIO.OUT)
    GPIO.output(pin_number, state)

@app.route('/pin/<string:position>/<string:couleur>/high', methods=['GET'])
def pin_HIGH(position, couleur):
    """Activer la couleur spécifiée à la position donnée."""
    try:
        if position in valid_positions:
            setup_and_activate(position, couleur, GPIO.HIGH)
            return jsonify(message="Cellule à la position {0} a été mise en {1}".format(position, couleur)), 200
        else:
            return jsonify(error="Position de cellule invalide"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/pin/<string:position>/<string:couleur>/low', methods=['GET'])
def pin_LOW(position, couleur):
    """Éteindre la couleur spécifiée à la position donnée."""
    try:
        if position in valid_positions:
            setup_and_activate(position, couleur, GPIO.LOW)
            return jsonify(message="Cellule à la position {0} : la couleur {1} a été éteinte".format(position, couleur)), 200
        else:
            return jsonify(error="Position de cellule invalide"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/reset', methods=['GET'])
def reset_all_pins():
    """Réinitialiser tous les pins GPIO à l'état bas (LOW)."""
    for position in led_matrix.values():
        for color_pin in position.values():
            GPIO.setup(color_pin, GPIO.OUT)
            GPIO.output(color_pin, GPIO.LOW)
    return jsonify({"message": "Tous les pins ont été réinitialisés à l'état LOW"}), 200

@app.route('/rainbow/<string:position>', methods=['GET'])
def rainbow(position):
    """Appliquer un effet arc-en-ciel à la position spécifiée."""
    try:
        if position in valid_positions:
            for couleur in ['red', 'green', 'blue', 'white']:
                setup_and_activate(position, couleur, GPIO.HIGH)
                time.sleep(0.1)
                setup_and_activate(position, couleur, GPIO.LOW)
            return jsonify(message="Effet arc-en-ciel appliqué à la position {0}".format(position)), 200
        else:
            return jsonify(error="Position de cellule invalide"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500

# Gestionnaires d'erreur pour les erreurs 404 et 500
@app.errorhandler(404)
def not_found(error):
    return jsonify(error="Non trouvé"), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(error="Erreur interne du serveur"), 500

# Point d'entrée principal pour exécuter l'application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
