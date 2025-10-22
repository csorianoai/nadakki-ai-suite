# INTEGRACIÓN COLLECTIONS EN APP.PY EXISTENTE

# Añadir estas líneas al final de tu app.py:

# ============================================================================
# COLLECTIONS INTEGRATION
# ============================================================================
try:
    from apps.collections.api.blueprint import collections_bp, register_collections_blueprint
    
    # Registrar Blueprint
    success = register_collections_blueprint(app)
    
    if success:
        app.logger.info("Collections module activated successfully")
        
        # Endpoint adicional de info
        @app.route('/api/v1/collections-info')
        def collections_info():
            return jsonify({
                "collections_enabled": True,
                "version": "3.1.0",
                "agentes": 36,
                "ecosistemas": 9,
                "compliance": "INDOTEL_DO",
                "integration_mode": "enterprise_extension"
            })
    else:
        app.logger.warning("Collections registration failed")
        
except ImportError:
    app.logger.info("Collections module not available")
except Exception as e:
    app.logger.error(f"Collections integration error: {e}")

# ============================================================================
