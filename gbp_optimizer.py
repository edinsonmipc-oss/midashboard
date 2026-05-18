#!/usr/bin/env python3
"""gbp_optimizer.py — Genera contenido optimizado para Google Business Profile
de Antonio PrimeScape Construction y Prime Property Maintenance.
Los resultados van al dashboard."""

import json, os
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))

GBP_DATA = {
    "antoniopaving": {
        "name": "Antonio PrimeScape Construction",
        "website": "https://antoniopaving.com",
        "phone": "0406 170 544",
        "address": "10 Elwood St, Notting Hill VIC 3168",
        "category": "Paving Contractor",
        "secondary_categories": [
            "Concrete Contractor",
            "Landscape Designer",
            "Driveway Contractor",
            "Stonemason"
        ],
        "description": "Antonio PrimeScape Construction es una empresa familiar con años de experiencia en pavimentación residencial y comercial en Melbourne. Especializados en calzadas de hormigón, exposed aggregate, pavimento permeable, piedra y ladrillo. Trabajamos con constructores, arquitectos y propietarios para entregar resultados de calidad superior. Servicio profesional, puntual y con presupuesto sin compromiso.",
        "services": [
            "Driveways / Calzadas de hormigón",
            "Exposed Aggregate / Hormigón pulido",
            "Permeable Paving / Pavimento permeable",
            "Stone & Brick Paving / Piedra y ladrillo",
            "Patios & Pool Decks",
            "Commercial Paving / Pavimentación comercial",
            "Concrete Pathways / Caminos de hormigón",
            "Retaining Walls / Muros de contención"
        ],
        "attributes": [
            "Free quote / Presupuesto gratis",
            "On-site estimate / Visita al sitio",
            "Fully insured / Seguro completo",
            "Family business / Empresa familiar",
            "Serving Melbourne since 2010+"
        ],
        "posts": [
            {
                "title": "🔥 Nuevo: Exposed Aggregate Driveway en Mulgrave",
                "body": "Terminamos este impresionante exposed aggregate driveway en Mulgrave. El cliente quedó encantado con el resultado. ¿Quieres algo similar? Contáctanos para un presupuesto gratis.",
                "cta": "Contact us",
                "link": "https://antoniopaving.com"
            },
            {
                "title": "☀️ Verano = Mejor época para pavimentar",
                "body": "El clima cálido es ideal para trabajos de hormigón y pavimentación. El material cura más rápido y el resultado es más duradero. Agenda tu proyecto ahora antes de que se llene la temporada.",
                "cta": "Get a quote",
                "link": "https://antoniopaving.com"
            },
            {
                "title": "🏗️ Trabajando con builders en Melbourne",
                "body": "Somos el partner de pavimentación para constructoras en Melbourne. Calidad, cumplimiento de plazos y precios competitivos. Si eres builder, contáctanos para tu próximo proyecto.",
                "cta": "Learn more",
                "link": "https://antoniopaving.com"
            },
            {
                "title": "🅿️ Transformación completa de entrada de auto",
                "body": "De entrada de tierra a una calzada de hormigón pulido. Valor +100% a tu propiedad. Invierte en tu casa con un driveway profesional.",
                "cta": "Get free quote",
                "link": "https://antoniopaving.com"
            }
        ],
        "review_request": "Hola [CLIENTE], gracias por confiar en Antonio PrimeScape Construction. Nos encantaría saber tu opinión. ¿Podés dejar una reseña en Google? https://search.google.com/local/writereview?placeid=TU_PLACE_ID_AQUI ¡Gracias!",
        "photo_guide": [
            "Antes/después de driveways (3-5 fotos)",
            "Fotos de exposed aggregate terminado (2-3)",
            "Proyectos comerciales (2-3)",
            "Equipo trabajando (1-2)",
            "Logo del negocio (1)"
        ]
    },
    "primeproperty": {
        "name": "Prime Property Maintenance",
        "website": "https://primepropertymaintenance.au",
        "phone": "0468 166 249",
        "address": "10 Elwood St, Notting Hill VIC 3168",
        "category": "Property Maintenance",
        "secondary_categories": [
            "Deck Builder",
            "Fence Contractor",
            "Pressure Washing Service",
            "Gutter Cleaning Service",
            "Landscaper",
            "Handyman",
            "Lawn Care Service"
        ],
        "description": "Prime Property Maintenance es su socio confiable en mantenimiento de propiedades en Melbourne. Ofrecemos servicios profesionales para propiedades comerciales y residenciales: decking, fencing, gutter cleaning, pressure washing, lawn mowing, y reparaciones generales. Trabajamos con agencias inmobiliarias, property managers y propietarios. Respuesta rápida, trabajos de calidad, precios justos.",
        "services": [
            "Decking & Deck Repairs / Deck de madera y compuesto",
            "Fencing / Cercas y cerramientos",
            "Gutter Cleaning / Limpieza de canaletas",
            "Pressure Washing / Hidrolavado",
            "Lawn Mowing & Gardening / Corte de césped y jardinería",
            "Handyman Services / Reparaciones generales",
            "Painting / Pintura interior y exterior",
            "Property Clean-up / Limpieza de propiedades"
        ],
        "attributes": [
            "Free quote / Presupuesto gratis",
            "Emergency service / Servicio de emergencia",
            "Fully insured / Seguro completo",
            "Serving Melbourne",
            "Response within 24h / Respuesta en 24hs"
        ],
        "posts": [
            {
                "title": "🧹 Gutter Cleaning antes del invierno",
                "body": "Las tormentas de invierno ya están cerca. No esperes a que las canaletas se tapen. Limpieza profesional de canaletas en toda Melbourne. Prevení filtraciones y daños.",
                "cta": "Book now",
                "link": "https://primepropertymaintenance.au"
            },
            {
                "title": "🪵 Nuevo deck en Glen Waverley",
                "body": "Terminamos este hermoso deck de madera compuesta en Glen Waverley. Sin mantenimiento, duradero, hermoso. Ideal para entretenimiento al aire libre.",
                "cta": "Get a quote",
                "link": "https://primepropertymaintenance.au"
            },
            {
                "title": "🏠 Property Managers: ¿Problemas con mantenimiento?",
                "body": "Respuesta rápida, un solo contacto para todos los servicios. Decking, fencing, gutter, pressure washing, handyman. Un equipo, múltiples servicios. Cotización gratis.",
                "cta": "Learn more",
                "link": "https://primepropertymaintenance.au"
            },
            {
                "title": "💧 Pressure Washing transforma tu propiedad",
                "body": "El hidrolavado profesional puede transformar una entrada, vereda o patio en horas. Resultados visibles al instante. Ideal para preparar propiedades para venta o alquiler.",
                "cta": "Get free quote",
                "link": "https://primepropertymaintenance.au"
            }
        ],
        "review_request": "Hola [CLIENTE], gracias por elegir Prime Property Maintenance. ¿Nos ayudas con una reseña en Google? https://search.google.com/local/writereview?placeid=TU_PLACE_ID_AQUI ¡Tu opinión nos ayuda a mejorar!",
        "photo_guide": [
            "Antes/después de decking (3-5 fotos)",
            "Antes/después de pressure washing (2-3)",
            "Trabajos de fencing (2-3)",
            "Equipo trabajando (1-2)",
            "Propiedades mantenidas (2-3)",
            "Logo del negocio (1)"
        ]
    }
}

def generate():
    output = {
        "updated": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "businesses": {}
    }
    
    for biz_id, data in GBP_DATA.items():
        biz_output = {
            "name": data["name"],
            "issues": [],
            "optimization": {
                "name": "✅ Correcto" if data["name"] else "⚠️ Revisar",
                "category": f"✅ {data['category']}",
                "secondary_categories": f"Agregar: {', '.join(data['secondary_categories'][:3])}...",
                "description": data["description"][:100] + "...",
                "services_count": len(data["services"]),
                "posts_ready": len(data["posts"]),
                "photo_guide": data["photo_guide"]
            },
            "action_plan": [
                f"Subir {len(data['photo_guide'])} fotos profesionales",
                "Agregar categorías secundarias en GBP",
                f"Publicar 1 post/semana (templates listos: {len(data['posts'])})",
                "Pedir reseñas a clientes satisfechos",
                "Responder a TODAS las reseñas en 24hs",
                "Actualizar horarios si es necesario",
                "Completar atributos del negocio"
            ],
            "posts": data["posts"],
            "review_template": data["review_request"],
            "description_full": data["description"]
        }
        output["businesses"][biz_id] = biz_output
    
    # Save
    path = os.path.join(DIR, "data", "gbp_optimization.json")
    with open(path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ GBP optimization data saved ({len(output['businesses'])} businesses)")
    print(f"   {path}")
    return output

if __name__ == "__main__":
    generate()
