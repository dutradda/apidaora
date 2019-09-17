{% for section in sections.keys() %}
{% for category in definitions.keys() if category in sections[section] %}
{% for text, _ in sections[section][category].items() %}
- {{ text }}
{% endfor %}
{% else %}
INVALID RELEASE - Changelog files was not found
{% endfor %}
{% endfor %}
