import glob
import inspect
from os.path import basename, join, splitext
import sys

from datalad import coreapi

def _get_github_reponame(super_dataset_path, name):
    super_ds = coreapi.Dataset(path=super_dataset_path)
    reponame = name

    if super_ds.id:
        github_sibling = next(iter(super_ds.siblings(name="github")), None)
        if github_sibling:
            super_reponame = splitext(basename(github_sibling["url"]))[0]
            reponame = join(super_reponame, name).rstrip('/').replace('/', '-')
        elif not reponame:
            origin_sibling = next(iter(super_ds.siblings(name="origin")), None)
            reponame = splitext(basename(github_sibling["url"]))[0]
    else:
        super_ds = None

    return reponame

def create(name, sibling="github"):
    super_ds = coreapi.Dataset(path=".")
    reponame = _get_github_reponame(".", name)

    if not super_ds.id:
        super_ds = None
    coreapi.create(path=name, dataset=super_ds)
    init_github(reponame, dataset=name, sibling=sibling)

def install(url, sibling="github"):
    url = url.rstrip('/')
    super_ds = coreapi.Dataset(path=".")
    name = splitext(basename(url))[0]
    reponame = _get_github_reponame(".", name)

    subdatasets = [sub_ds["gitmodule_name"] for sub_ds in super_ds.subdatasets()]
    if url in subdatasets:
        coreapi.install(path=url)
    else:
        coreapi.install(source=url)

    init_github(reponame, dataset=name, sibling=sibling)

def install_subdatasets(sibling="github"):
    coreapi.install(path=".", recursive=True)
    reponame = _get_github_reponame(".", "")
    init_github(reponame, dataset=".", sibling=sibling)

def publish(path="*", sibling="github"):
    coreapi.add(path=glob.glob(path), recursive=True)
    coreapi.save()
    coreapi.publish(to=sibling, recursive=True)

def update(sibling="github"):
    coreapi.update(sibling=sibling, recursive=True, merge=True)

def init_github(name, login=None, dataset=".", sibling="github"):
    dataset = coreapi.Dataset(path=dataset)
    coreapi.create_sibling_github(name, dataset=dataset, name=sibling,
        github_login=login, recursive=True, access_protocol="ssh",
        existing="reconfigure")
    coreapi.siblings(dataset=dataset, name=sibling, publish_by_default="master")

if __name__ == "__main__":
    # get the second argument from the command line
    fct_name = sys.argv[1]

    # get pointers to the objects based on the string names
    fct = globals()[fct_name]

    # pass all the parameters from the third until the end of
    # what the function needs & ignore the rest
    args = inspect.getargspec(fct)
    params = sys.argv[2:len(args[0]) + 2]
    fct(*params)
