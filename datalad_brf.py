import glob
import inspect
from os.path import basename, join, splitext
import sys

from datalad import coreapi
from datalad.support.exceptions import IncompleteResultsError

def _get_github_reponame(dataset_path, name=""):
    dataset = coreapi.Dataset(path=dataset_path)
    reponame_buffer = [name]

    while dataset.id:
        reponame_buffer.insert(0, basename(dataset.path))
        dataset = coreapi.Dataset(path=join(dataset.path, ".."))

    return '-'.join(reponame_buffer).rstrip('-')

def create(name, sibling="origin"):
    super_ds = coreapi.Dataset(path=".")
    coreapi.create(path=name, dataset=super_ds if super_ds.id else None)

    if sibling == "github":
        reponame = _get_github_reponame(".", name)
        init_github(reponame, dataset=name, sibling=sibling)

def install(url, name=None, sibling="origin"):
    url = url.rstrip('/')
    if name is None:
        name = splitext(basename(url))[0]

    reponame = _get_github_reponame(".", name)

    if not install_subdatasets_tree(url):
        coreapi.install(name, source=url)

    if sibling == "github":
        init_github(reponame, dataset=name, sibling=sibling)

def install_subdatasets_tree(url, sibling="origin"):
    url = url.rstrip('/')
    subdatasets_tree = url.split('/')

    super_ds = coreapi.Dataset(path=".")
    subdatasets = [sub_ds["gitmodule_name"] for sub_ds in super_ds.subdatasets()]
    if next(iter(subdatasets_tree), None) not in subdatasets:
        return False

    base_name = subdatasets_tree[0]
    reponame = _get_github_reponame(".", base_name)

    dataset_path = "."
    while subdatasets_tree:
        name = subdatasets_tree.pop(0)

        dataset = coreapi.Dataset(path=dataset_path)
        subdatasets = [sub_ds["gitmodule_name"] for sub_ds in dataset.subdatasets()]
        if name not in subdatasets:
            break

        try:
            coreapi.install(path=join(dataset_path, name), dataset=dataset,
                on_failure="stop")
        except IncompleteResultsError as error:
            github_sibling = next(iter(dataset.siblings(name="github")), None)
            if github_sibling:
                path = join(dataset_path, name)
                source = '-'.join([splitext(github_sibling["url"])[0], name + ".git"])
                coreapi.install(path=path, dataset=dataset, source=source)
                coreapi.siblings("add", dataset=path, name="github", url=source)
                coreapi.siblings("remove", dataset=path, name="origin")
            else:
                raise error

        dataset_path = join(dataset_path, name)

    if sibling == "github":
        init_github(reponame, dataset=base_name, sibling=sibling)

    return True

def install_subdatasets(sibling="origin"):
    coreapi.install(path=".", recursive=True)
    reponame = _get_github_reponame(".")
    if sibling == "github":
        init_github(reponame, dataset=".", sibling=sibling)

def publish(path="*", sibling="origin"):
    coreapi.add(path=glob.glob(path), recursive=True)
    coreapi.save()
    coreapi.publish(to=sibling, recursive=True)

def update(sibling="origin"):
    coreapi.update(sibling=sibling, recursive=True, merge=True)

def init_github(name=None, login=None, dataset=".", sibling="github"):
    if name is None:
        name = _get_github_reponame(dataset)
    dataset = coreapi.Dataset(path=dataset)
    coreapi.create_sibling_github(name, dataset=dataset, name=sibling,
        github_login=login, recursive=False, access_protocol="ssh",
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
