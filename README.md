# NX Sucursales

> **Propiedad de [Nimetrix](https://www.nimetrix.com/)** - Todos los derechos reservados.

Módulos para gestión de múltiples sucursales/unidades operativas en Odoo 18, permitiendo manejar varias sucursales dentro de una misma compañía.

## Autor Original

**BrowseInfo**
Website: https://www.browseinfo.in

## Módulo Principal

### branch
Módulo base para operación multi-sucursal.

**Características:**
- Gestión de múltiples sucursales por compañía
- Filtrado de datos por sucursal
- Asignación de usuarios a sucursales
- Segregación de operaciones por sucursal

**Áreas cubiertas:**
- Ventas
- Compras
- Inventario (almacenes, ubicaciones, movimientos)
- Contabilidad (facturas, pagos, diarios)
- Productos y listas de precios

**Dependencias:** `base`, `sale_management`, `purchase`, `stock`, `account`, `purchase_stock`, `web`, `stock_account`, `nimetrix_municipal_taxes`

## Módulos Adicionales

| Módulo | Descripción |
|--------|-------------|
| `branch_analytic_account` | Cuentas analíticas por sucursal |
| `bi_branch_pos` | Punto de venta por sucursal |
| `bi_branch_scrap_order` | Órdenes de desecho por sucursal |
| `bi_odoo_mrp_multi_branch` | Manufactura multi-sucursal |
| `bi_odoo_multi_branch_hr` | Recursos humanos multi-sucursal |
| `bi_branch_budget_ent` | Presupuestos por sucursal (Enterprise) |

## Arquitectura

```
nx_sucursales/
├── branch/                    # Módulo base multi-sucursal
├── branch_analytic_account/   # Cuentas analíticas
├── bi_branch_pos/             # POS multi-sucursal
├── bi_branch_scrap_order/     # Desechos por sucursal
├── bi_odoo_mrp_multi_branch/  # Manufactura
├── bi_odoo_multi_branch_hr/   # RRHH
└── bi_branch_budget_ent/      # Presupuestos
```

## Funcionalidades

### Ventas
- Órdenes de venta filtradas por sucursal
- Facturación por sucursal
- Reportes de venta por sucursal

### Compras
- Órdenes de compra por sucursal
- Recepción de mercancía por sucursal

### Inventario
- Almacenes asignados a sucursales
- Movimientos de stock segregados
- Valoración de inventario por sucursal

### Contabilidad
- Diarios contables por sucursal
- Pagos y cobros por sucursal
- Reportes financieros por sucursal

### Punto de Venta
- Configuración de POS por sucursal
- Sesiones y cierres por sucursal

## Requisitos

- Odoo 18
- Módulo `nimetrix_municipal_taxes` (nx_localizacion)
- Módulos base de Odoo: `sale_management`, `purchase`, `stock`, `account`

## Instalación

1. Asegurarse de tener instalado `nx_localizacion`

2. Clonar el repositorio:
   ```bash
   git submodule add <url-repositorio> addons/nx_sucursales
   ```

3. Reiniciar Odoo:
   ```bash
   docker compose restart odoo
   ```

4. Instalar el módulo `branch` primero

5. Instalar módulos adicionales según necesidad

## Configuración

1. Ir a **Configuración > Sucursales**
2. Crear las sucursales de la compañía
3. Asignar usuarios a cada sucursal
4. Configurar almacenes por sucursal
5. Configurar diarios contables por sucursal

## Seguridad

El módulo implementa reglas de registro (ir.rule) para filtrar automáticamente los datos según la sucursal del usuario conectado.

## Licencia

OPL-1 (Odoo Proprietary License)
