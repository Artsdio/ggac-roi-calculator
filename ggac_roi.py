─── FILE UPLOADER (MODIFIED SECTION) ────────────────────────────────────────
with st.expander("📂 Import dari Excel — Modal_GGAC_v3.xlsx", expanded=False):
    st.markdown(
        "Upload file `Modal_GGAC_v3.xlsx` untuk mengisi otomatis nilai investasi & "
        "modal pengelola di sidebar. Ubah angka di Excel → simpan → upload ulang → "
        "semua input terupdate."
    )
    uploaded = st.file_uploader(
        "Pilih file Modal_GGAC_v3.xlsx", type=["xlsx"],
        key="modal_upload", label_visibility="collapsed"
    )
    xl_data = {}
    if uploaded is not None:
        try:
            xl_data = parse_modal_excel(uploaded.read())

            # ── Pilih fase ────────────────────────────────────────────────
            fase_pilihan = st.radio(
                "Hitung ROI untuk fase mana?",
                ["Fase 1 saja (operasional sekarang)",
                 "Fase 1 + Fase 2 (setelah scale-up)"],
                horizontal=True, key="fase_radio"
            )
            inv_aktif = (xl_data.get("investasi_f1", 0)
                         if "Fase 1 saja" in fase_pilihan
                         else xl_data.get("investasi_f12", 0))
            xl_data["investasi"]  = inv_aktif
            xl_data["fase_label"] = ("Fase 1 — Prioritas/Urgent"
                                     if "Fase 1 saja" in fase_pilihan
                                     else "Fase 1 + Fase 2 — Termasuk Pengembangan")

            # ── Ambil nilai dari Excel ─────────────────────────────────────
            gym_f1  = xl_data.get("sub_fase1", 0)      # E10 = 44.960.000
            gym_f2  = xl_data.get("sub_fase2", 0)      # E18 = 0 (Qty=0)
            pen     = xl_data.get("sub_pend", 0)       # E28 = 13.300.000
            buf_pct = xl_data.get("buffer_pct", 0.10)  # E36 = 0.10
            total_f1  = xl_data.get("investasi_f1", 0) # B37 = 64.086.000
            total_f12 = xl_data.get("investasi_f12", 0)# C37 = 75.592.000
            mp      = xl_data.get("modal_pengelola", 0)

            # Hitung buffer yang benar
            subtotal_f1 = gym_f1 + pen
            buffer_f1   = round(subtotal_f1 * buf_pct)

            subtotal_f12 = gym_f1 + gym_f2 + pen
            buffer_f12   = round(subtotal_f12 * buf_pct)

            # ── Ringkasan modal — PERBAIKAN TAMPILAN ──────────────────────
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.markdown(f"""
                 <div style="background:#E8F5EE;border-radius:10px;padding:1rem;
                            border-left:4px solid #0F6E56">
                   <div style="font-size:11px;color:#888780;font-weight:600;
                              text-transform:uppercase">Investasi Fase 1 (aktif)</div>
                   <div style="font-size:20px;font-weight:700;color:#0F6E56;
                              font-family:monospace;margin:8px 0">
                     Rp {rp(total_f1)}
                   </div>
                   <div style="font-size:11px;color:#888780;line-height:1.8">
                     <div style="display:flex;justify-content:space-between">
                       <span>Peralatan gym Fase 1</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         Rp {rp(gym_f1)}
                       </span>
                     </div>
                     <div style="display:flex;justify-content:space-between">
                       <span>Fasilitas penunjang</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         Rp {rp(pen)}
                       </span>
                     </div>
                     <div style="display:flex;justify-content:space-between;
                                 border-top:1px solid #ccc;margin-top:4px;padding-top:4px">
                       <span>Subtotal</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         Rp {rp(subtotal_f1)}
                       </span>
                     </div>
                     <div style="display:flex;justify-content:space-between;color:#0F6E56">
                       <span>Buffer {int(buf_pct*100)}%</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         Rp {rp(buffer_f1)}
                       </span>
                     </div>
                   </div>
                   <div style="font-size:11px;color:#0F6E56;font-weight:600;
                              margin-top:8px;padding-top:8px;border-top:2px solid #0F6E56">
                     TOTAL: Rp {rp(total_f1)}
                   </div>
                 </div>""", unsafe_allow_html=True)

            with col_s2:
                st.markdown(f"""
                 <div style="background:#FFF8E7;border-radius:10px;padding:1rem;
                            border-left:4px solid #854F0B">
                   <div style="font-size:11px;color:#888780;font-weight:600;
                              text-transform:uppercase">Fase 2 (pengembangan)</div>
                   <div style="font-size:20px;font-weight:700;color:#854F0B;
                              font-family:monospace;margin:8px 0">
                     Rp {rp(gym_f2)}
                   </div>
                   <div style="font-size:11px;color:#888780;line-height:1.8">
                     <div style="display:flex;justify-content:space-between">
                       <span>{len(xl_data.get('fase2_aktif',[]))} item aktif</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         {len(xl_data.get('fase2_gym',[]))} total item
                       </span>
                     </div>
                     <div style="display:flex;justify-content:space-between">
                       <span>Subtotal Fase 1+2</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         Rp {rp(subtotal_f12)}
                       </span>
                     </div>
                     <div style="display:flex;justify-content:space-between;color:#854F0B">
                       <span>Buffer {int(buf_pct*100)}%</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         Rp {rp(buffer_f12)}
                       </span>
                     </div>
                   </div>
                   <div style="font-size:11px;color:#854F0B;font-weight:600;
                              margin-top:8px;padding-top:8px;border-top:2px solid #854F0B">
                     TOTAL FASE 1+2: Rp {rp(total_f12)}
                   </div>
                 </div>""", unsafe_allow_html=True)

            with col_s3:
                st.markdown(f"""
                 <div style="background:#EDF3FB;border-radius:10px;padding:1rem;
                            border-left:4px solid #185FA5">
                   <div style="font-size:11px;color:#888780;font-weight:600;
                              text-transform:uppercase">Modal Pengelola (Pihak II)</div>
                   <div style="font-size:20px;font-weight:700;color:#185FA5;
                              font-family:monospace;margin:8px 0">
                     Rp {rp(mp)}
                   </div>
                   <div style="font-size:11px;color:#888780;line-height:1.8">
                     <div style="display:flex;justify-content:space-between">
                       <span>Nilai buku peralatan</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         {len(xl_data.get('peralatan',[]))} item
                       </span>
                     </div>
                     <div style="display:flex;justify-content:space-between">
                       <span>Periode hitung</span>
                       <span style="font-family:DM Mono,monospace;font-weight:600">
                         per 2026
                       </span>
                     </div>
                   </div>
                   <div style="font-size:11px;color:#185FA5;font-weight:600;
                              margin-top:8px;padding-top:8px;border-top:2px solid #185FA5">
                     IN-KIND CONTRIBUTION
                   </div>
                 </div>""", unsafe_allow_html=True)

            st.success(
                f"✅ Terbaca. "
                f"ROI dihitung untuk: **{'Fase 1' if 'Fase 1 saja' in fase_pilihan else 'Fase 1+2'}** · "
                f"Investasi owner: **Rp {rp(inv_aktif)}** · "
                f"Modal pengelola: **Rp {rp(mp)}**"
            )

            # ── Detail tables (tetap sama) ──────────────────────────────────
            tab_f1, tab_f2, tab_pen, tab_alat = st.tabs([
                " Fase 1 (aktif)", "🟡 Fase 2 (pengembangan)",
                " Penunjang", "🔧 Alat Pengelola"
            ])

            def show_items(tab, items, label):
                with tab:
                    if items:
                        df = pd.DataFrame(items)
                        df["harga"] = df["harga"].apply(lambda x: f"Rp {rp(x)}")
                        df["total"] = df["total"].apply(lambda x: f"Rp {rp(x)}")
                        df["qty_str"] = df["qty"].apply(
                            lambda x: str(x) if x > 0 else "0 *(belum dibeli)*")
                        st.dataframe(
                            df[["nama", "qty_str", "harga", "total"]].rename(columns={
                                "nama": "Item", "qty_str": "Qty",
                                "harga": "Harga Satuan", "total": "Total"}),
                            use_container_width=True)
                    else:
                        st.caption(f"Tidak ada item {label}.")

            show_items(tab_f1, xl_data.get("fase1_gym",[]), "Fase 1")
            show_items(tab_f2, xl_data.get("fase2_gym",[]), "Fase 2")
            show_items(tab_pen, xl_data.get("pend_items",[]), "penunjang")

            with tab_alat:
                alat = xl_data.get("peralatan",[])
                if alat:
                    df_a = pd.DataFrame(alat)
                    df_a["harga"] = df_a["harga"].apply(lambda x: f"Rp {rp(x)}")
                    df_a["nb"]    = df_a["nb"].apply(lambda x: f"Rp {rp(x)}")
                    st.dataframe(
                        df_a[["nama", "thn", "harga", "nb"]].rename(columns={
                            "nama": "Alat", "thn": "Thn Beli",
                            "harga": "Harga Beli", "nb": "Nilai Buku 2026"}),
                        use_container_width=True)

        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")
            xl_data = {}