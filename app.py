import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Cuenta Corriente Comercial",
    page_icon="💼",
    layout="wide"
)

st.title("Cuenta Corriente Comercial")
st.caption("Draft app para registrar movimientos con cabecera, detalle y totales.")


def to_float(value):
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def calcular_subtotal_linea(row):
    cantidad = to_float(row.get("cantidad", 0))
    importe = to_float(row.get("importe", 0))
    dto = to_float(row.get("dto", 0))
    tasa1 = to_float(row.get("tasa1", 0))
    tasa2 = to_float(row.get("tasa2", 0))

    # dto tratado como porcentaje
    subtotal = ((cantidad * importe) * (dto / 100.0)) + tasa1 + tasa2
    return round(subtotal, 2)


if "detalle_df" not in st.session_state:
    st.session_state.detalle_df = pd.DataFrame([
        {
            "descripcion": "",
            "cantidad": 0.0,
            "importe": 0.0,
            "dto": 0.0,
            "tasa1": 0.0,
            "tasa2": 0.0,
            "subtotal_linea": 0.0,
        }
    ])


st.subheader("Cabecera")

col1, col2, col3 = st.columns(3)
with col1:
    proveedor = st.text_input("Proveedor")
with col2:
    fecha = st.date_input("Fecha", value=date.today())
with col3:
    fecha_pago = st.date_input("Fecha de pago", value=date.today())

col4, col5 = st.columns(2)
with col4:
    tipo_movimiento = st.selectbox(
        "Tipo de movimiento",
        ["Factura", "Nota de Débito", "Nota de Crédito", "Recibo", "Otro"]
    )
with col5:
    referencia = st.text_input("Referencia")

st.divider()

st.subheader("Detalle")

edited_df = st.data_editor(
    st.session_state.detalle_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "descripcion": st.column_config.TextColumn("Descripción"),
        "cantidad": st.column_config.NumberColumn("Cantidad", step=1.0, format="%.2f"),
        "importe": st.column_config.NumberColumn("Importe", step=0.01, format="%.2f"),
        "dto": st.column_config.NumberColumn("Dto (%)", step=0.01, format="%.2f"),
        "tasa1": st.column_config.NumberColumn("Tasa 1", step=0.01, format="%.2f"),
        "tasa2": st.column_config.NumberColumn("Tasa 2", step=0.01, format="%.2f"),
        "subtotal_linea": st.column_config.NumberColumn(
            "Subtotal línea",
            disabled=True,
            format="%.2f"
        ),
    },
    key="detalle_editor"
)

for idx in edited_df.index:
    edited_df.at[idx, "subtotal_linea"] = calcular_subtotal_linea(edited_df.loc[idx])

st.session_state.detalle_df = edited_df.copy()

st.dataframe(
    st.session_state.detalle_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("Totales")

sum_subtotal_linea = round(st.session_state.detalle_df["subtotal_linea"].fillna(0).sum(), 2)

col6, col7, col8, col9 = st.columns(4)
with col6:
    st.number_input(
        "Suma subtotal línea",
        value=float(sum_subtotal_linea),
        disabled=True,
        format="%.2f"
    )
with col7:
    impuesto1 = st.number_input("Impuesto 1", step=0.01, format="%.2f")
with col8:
    impuesto2 = st.number_input("Impuesto 2", step=0.01, format="%.2f")
with col9:
    total = round(sum_subtotal_linea + impuesto1 + impuesto2, 2)
    st.number_input(
        "Total",
        value=float(total),
        disabled=True,
        format="%.2f"
    )

st.divider()

st.subheader("Vista previa del movimiento")

payload = {
    "cabecera": {
        "proveedor": proveedor,
        "fecha": str(fecha),
        "fecha_pago": str(fecha_pago),
        "tipo_movimiento": tipo_movimiento,
        "referencia": referencia,
    },
    "detalle": st.session_state.detalle_df.to_dict(orient="records"),
    "totales": {
        "sum_subtotal_linea": sum_subtotal_linea,
        "impuesto1": impuesto1,
        "impuesto2": impuesto2,
        "total": total,
    }
}

st.json(payload)

if st.button("Guardar movimiento"):
    st.success("Movimiento listo para guardar. Ahora mismo está en modo draft.")
