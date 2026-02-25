import streamlit as st
import pandas as pd
import os

# Configuración de la App de Lorena
st.set_page_config(page_title="LoreV Uniformes", layout="wide")

# Archivos de datos
DB_CAT, DB_INV, DB_CLI, DB_VEN, DB_ABO = "catalogo.csv", "database.csv", "clientes.csv", "ventas.csv", "abonos.csv"

def cargar(archivo, columnas):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            return df if not df.empty else pd.DataFrame(columns=columnas)
        except: return pd.DataFrame(columns=columnas)
    return pd.DataFrame(columns=columnas)

st.title("✨ LoreV - Gestión de Uniformes")
st.write("Control de inventario y ventas para Lorena Vargas")

tabs = st.tabs(["📋 Catálogo", "📦 Inventario", "👥 Clientes", "💰 Ventas", "💸 Abonos"])

# --- PESTAÑA 1: CATÁLOGO ---
with tabs[0]:
    st.header("Maestro de Precios")
    df_cat = cargar(DB_CAT, ["Nombre", "Precio Compra", "Precio Venta"])
    with st.form("f_cat", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        n = c1.text_input("Nombre de la Prenda")
        pc = c2.number_input("Costo Compra", min_value=0)
        pv = c3.number_input("Precio Venta", min_value=0)
        if st.form_submit_button("Guardar en Catálogo"):
            if n:
                pd.DataFrame([[n,pc,pv]], columns=df_cat.columns).to_csv(DB_CAT, mode='a', header=not os.path.exists(DB_CAT), index=False)
                st.rerun()
    st.dataframe(df_cat, use_container_width=True)
    
    # ZONA DE BORRADO
    if not df_cat.empty:
        with st.expander("🗑️ Corregir/Borrar Producto del Catálogo"):
            prod_del = st.selectbox("Seleccione producto para eliminar", df_cat["Nombre"].tolist())
            if st.button("Eliminar permanentemente del Catálogo"):
                df_cat = df_cat[df_cat["Nombre"] != prod_del]
                df_cat.to_csv(DB_CAT, index=False)
                st.rerun()

# --- PESTAÑA 2: INVENTARIO ---
with tabs[1]:
    st.header("Cargue de Tallas y Stock")
    df_cat = cargar(DB_CAT, ["Nombre", "Precio Compra", "Precio Venta"])
    df_inv = cargar(DB_INV, ["Producto", "Talla", "Color", "Cantidad", "Precio Venta"])
    if df_cat.empty: st.warning("Agrega productos al Catálogo primero.")
    else:
        with st.form("f_inv", clear_on_submit=True):
            p_s = st.selectbox("Producto", df_cat["Nombre"].tolist())
            t = st.selectbox("Talla", ["6","8","10","12","14","16","S","M","L","XL"])
            col = st.text_input("Color")
            can = st.number_input("Cantidad", min_value=1)
            if st.form_submit_button("Cargar a Inventario"):
                pv = df_cat.loc[df_cat["Nombre"] == p_s, "Precio Venta"].values[0]
                mask = (df_inv['Producto'] == p_s) & (df_inv['Talla'].astype(str) == str(t)) & (df_inv['Color'] == col)
                if mask.any():
                    df_inv.at[df_inv.index[mask][0], 'Cantidad'] += can
                    df_inv.to_csv(DB_INV, index=False)
                else:
                    pd.DataFrame([[p_s,t,col,can,pv]], columns=df_inv.columns).to_csv(DB_INV, mode='a', header=not os.path.exists(DB_INV), index=False)
                st.rerun()
    st.dataframe(df_inv, use_container_width=True)
    
    if not df_inv.empty:
        with st.expander("🗑️ Corregir/Borrar Stock"):
            idx_del = st.number_input("Ingrese el número de fila a borrar (columna izquierda)", min_value=0, max_value=len(df_inv)-1)
            if st.button("Eliminar fila de inventario"):
                df_inv = df_inv.drop(df_inv.index[idx_del])
                df_inv.to_csv(DB_INV, index=False)
                st.rerun()

# --- PESTAÑA 3: CLIENTES ---
with tabs[2]:
    st.header("Directorio de Clientes")
    df_cli = cargar(DB_CLI, ["Nombre","Telefono","Saldo"])
    with st.form("f_cli", clear_on_submit=True):
        n, t = st.text_input("Nombre"), st.text_input("Teléfono")
        if st.form_submit_button("Registrar Cliente"):
            pd.DataFrame([[n,t,0.0]], columns=["Nombre","Telefono","Saldo"]).to_csv(DB_CLI, mode='a', header=not os.path.exists(DB_CLI), index=False)
            st.rerun()
    st.dataframe(df_cli, use_container_width=True)
    
    if not df_cli.empty:
        with st.expander("🗑️ Corregir/Borrar Cliente"):
            cli_del = st.selectbox("Seleccione cliente para eliminar", df_cli["Nombre"].tolist())
            if st.button("Eliminar Cliente"):
                df_cli = df_cli[df_cli["Nombre"] != cli_del]
                df_cli.to_csv(DB_CLI, index=False)
                st.rerun()

# --- PESTAÑA 4: VENTAS ---
with tabs[3]:
    st.header("Registro de Ventas")
    df_inv = cargar(DB_INV, ["Producto", "Talla", "Color", "Cantidad", "Precio Venta"])
    df_cli = cargar(DB_CLI, ["Nombre", "Telefono", "Saldo"])
    df_ven = cargar(DB_VEN, ["Cliente","Producto","Cant","Total","Metodo"])
    disp = df_inv[df_inv["Cantidad"] > 0]
    
    if disp.empty or df_cli.empty: st.warning("Sin stock o clientes.")
    else:
        with st.form("f_v"):
            cl = st.selectbox("Cliente", df_cli["Nombre"].tolist())
            ops = (disp["Producto"].astype(str) + " (" + disp["Talla"].astype(str) + "-" + disp["Color"].astype(str) + ")").tolist()
            ps = st.selectbox("Prenda", ops)
            idx = disp.index[ops.index(ps)]
            ct = st.number_input("Cantidad", min_value=1, max_value=int(df_inv.at[idx, 'Cantidad']))
            mp = st.selectbox("Pago", ["Efectivo", "Transferencia", "Crédito"])
            if st.form_submit_button("Finalizar Venta"):
                tot = df_inv.at[idx, "Precio Venta"] * ct
                df_inv.at[idx, "Cantidad"] -= ct
                df_inv.to_csv(DB_INV, index=False)
                if mp == "Crédito":
                    idx_c = df_cli[df_cli["Nombre"] == cl].index[0]
                    df_cli.at[idx_c, "Saldo"] += tot
                    df_cli.to_csv(DB_CLI, index=False)
                pd.DataFrame([[cl, ps, ct, tot, mp]], columns=df_ven.columns).to_csv(DB_VEN, mode='a', header=not os.path.exists(DB_VEN), index=False)
                st.rerun()
    st.dataframe(df_ven, use_container_width=True)
    
    if not df_ven.empty:
        with st.expander("🗑️ Anular última venta"):
            st.write("Esto borrará el registro de la venta, pero NO devuelve el stock ni quita la deuda automáticamente.")
            if st.button("Borrar última fila de ventas"):
                df_ven = df_ven[:-1]
                df_ven.to_csv(DB_VEN, index=False)
                st.rerun()

# --- PESTAÑA 5: ABONOS ---
with tabs[4]:
    st.header("Control de Pagos")
    df_cli = cargar(DB_CLI, ["Nombre","Telefono","Saldo"])
    df_abo = cargar(DB_ABO, ["Cliente","Monto","Resta"])
    deud = df_cli[df_cli["Saldo"] > 0]
    if deud.empty: st.info("Sin deudas pendientes.")
    else:
        c_a = st.selectbox("Seleccione Deudor", deud["Nombre"].tolist())
        d = float(df_cli.loc[df_cli["Nombre"] == c_a, "Saldo"].values[0])
        st.metric("Debe actualmente", f"${d:,.0f}")
        m = st.number_input("Valor del abono", min_value=0.0, max_value=d, step=1000.0)
        st.info(f"Nuevo saldo tras pago: **${d - m:,.0f}**")
        if st.button("Registrar Pago"):
            df_cli.at[df_cli[df_cli["Nombre"] == c_a].index[0], "Saldo"] -= m
            df_cli.to_csv(DB_CLI, index=False)
            pd.DataFrame([[c_a, m, d-m]], columns=df_abo.columns).to_csv(DB_ABO, mode='a', header=not os.path.exists(DB_ABO), index=False)
            st.rerun()
    st.dataframe(df_abo, use_container_width=True)