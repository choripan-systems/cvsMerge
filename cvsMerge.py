import pandas as pd
import matplotlib.pyplot as plt
import argparse

def merge_same_metric(args):
    file1_path = args.in_file1
    file2_path = args.in_file2
    output_csv = args.out_file
    output_plot = args.plot_file

    try:
        # Helper function to read messy CSVs
        def robust_read(path):
            # sep=None + engine='python' tells pandas to guess the separator (comma, semicolon, etc.)
            # on_bad_lines='skip' will ignore those header/title rows that cause the error
            df = pd.read_csv(path, encoding='ISO-8859-1', sep=None, engine='python', on_bad_lines='skip')
            
            # If the first column is mostly text/metadata, we might need to drop it.
            # Here we ensure we only keep numeric data rows
            df = df.apply(pd.to_numeric, errors='coerce').dropna()
            return df

        # 1. Load the files
        data1 = robust_read(file1_path)
        data2 = robust_read(file2_path)

        # 2. Map columns (Column 0 = Distance/X, Column 1 = Speed/Y)
        df1 = pd.DataFrame({'X': data1.iloc[:, 0], 'Y1': data1.iloc[:, 1]})
        df2 = pd.DataFrame({'X': data2.iloc[:, 0], 'Y2': data2.iloc[:, 1]})

        # 3. Merge on 'X'
        merged_df = pd.merge(df1, df2, on='X', how='outer')

        # 4. Sort and Interpolate
        merged_df = merged_df.sort_values(by='X').reset_index(drop=True)
        merged_df[['Y1', 'Y2']] = merged_df[['Y1', 'Y2']].interpolate(method='linear', limit_direction='both')

        # 5. Save and Plot
        merged_df.to_csv(output_csv, index=False)

        if output_plot:
            plt.figure(figsize=(24, 12))
            plt.plot(merged_df['X'], merged_df['Y1'], label='File 1 (MG)', alpha=0.8)
            plt.plot(merged_df['X'], merged_df['Y2'], label='File 2 (VG)', alpha=0.8, linestyle='--')
            plt.xlabel(args.x_axis_label)
            plt.ylabel(args.y_axis_label)
            if args.plot_title:
                plt.title(args.plot_title)
            plt.legend()
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.tight_layout()
            plt.savefig(output_plot)
        
        print(f"Success! CSV saved as {output_csv}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog = 'cvsMerge',
        description="A tool for merging two CVS data files and optionally graph the merged data"
    )
    parser.add_argument(
        '--in-file1',
        type=str,
        help="Path to the first input CVS file"
    )
    parser.add_argument(
        '--in-file2',
        type=str,
        help="Path to the second input CVS file"
    )
    parser.add_argument(
        '--out-file',
        type=str,
        help="Path to the merged output CVS file"
    )
    parser.add_argument(
        '--plot-file',
        type=str,
        default=None,
        help="Path to the merged output PNG file"
    )    
    parser.add_argument(
        '--plot-title',
        type=str,
        default=None,
        help="Title of the plot"
    )
    parser.add_argument(
        '--x-axis-label',
        type=str,
        default='X',
        help="Label for the plot's X-axis"
    )
    parser.add_argument(
        '--y-axis-label',
        type=str,
        default='Y',
        help="Label for the plot's Y-axis"
    )

    args = parser.parse_args()
    merge_same_metric(args)
    

if __name__ == "__main__":
    main()

