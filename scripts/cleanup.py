import kaggle
import time

def datatalk_cleanup():
    api = kaggle.api
    api.authenticate()
    user_id = api.get_config_value('username')

    print(f"🧹 Starting cleanup for user: {user_id}")

    # 1. CLEANUP KERNELS (Notebooks)
    # Lists your private kernels and filters for 'datatalk-'
    kernels = api.kernels_list(user=user_id, privacy='private')
    for kernel in kernels:
        if 'datatalk-run-' in kernel.ref:
            try:
                # Note: Currently, the API deletion requires the slug format [user]/[slug]
                api.kernels_delete(kernel.ref)
                print(f"✅ Deleted Kernel: {kernel.ref}")
            except Exception as e:
                print(f"⚠️ Could not delete kernel {kernel.ref}: {e}")

    # 2. CLEANUP DATASETS
    # Filters for your auto-generated datasets
    datasets = api.dataset_list(user=user_id, mine=True)
    for ds in datasets:
        if 'datatalk-ds-' in ds.ref:
            try:
                api.dataset_delete(ds.ref)
                print(f"✅ Deleted Dataset: {ds.ref}")
            except Exception as e:
                print(f"⚠️ Could not delete dataset {ds.ref}: {e}")

    print("✨ Cleanup Finished!")

if __name__ == "__main__":
    datatalk_cleanup()