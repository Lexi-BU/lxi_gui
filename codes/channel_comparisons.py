key_list = ["Channel1", "Channel2", "Channel3", "Channel4"]
try:
    df_sci_q = df_sci_q[df_sci_q.IsCommanded==True]
except:
    pass
for key in df_sci_n.keys():
    try:
        plt.figure()
        plt.plot(df_sci_q.index, df_sci_q[key], 'r.', ms=1, label='q')
        plt.plot(df_sci_n.index/1e3, df_sci_n[key], 'b.', ms=1, label='n')
        plt.xlabel("Time (seconds)")
        plt.ylabel("Voltage (V)")

        plt.legend()
        plt.title(f"Comparison for {key} voltages")
        plt.savefig(f"../figures/{key}_comparison_v4.png")
        plt.close("all")
        print(f"Saved {key} comparison figure")
    except:
        print(f"Could not plot {key}")
        pass
for key in df_hk_n.keys():
    try:
        plt.figure()
        plt.plot(df_hk_q.index, df_hk_q[key], 'r.', ms=1, label='q')
        plt.plot(df_hk_n.index/1e3, df_hk_n[key], 'b.', ms=1, label='n')
        plt.xlabel("Time (seconds)")
        plt.ylabel("")

        plt.legend()
        plt.title(f"Comparison for {key}")
        plt.savefig(f"../figures/{key}_comparison_v4.png")
        plt.close("all")
        print(f"Saved {key} comparison figure")
    except:
        print(f"Could not plot {key}")
        pass