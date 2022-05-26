import argparse
import pathlib
import subprocess
import sys
import os

def run(*args):
	"""Runs the specified command."""
	ret = subprocess.Popen(args).wait()
	if (0 != ret):
		sys.exit(ret)

class host_t:
	"""The host class."""
	def __del__(self):
		"""The destructor."""
		pass

	def __init__(self, user_args):
		"""The main constructor."""
		#---Call parent constructor---#
		super().__init__()

		#---Zero---#
		self.install_pfx			= user_args.install_pfx.absolute()
		self.build_shared_libs		= user_args.build_shared_libs

	def configure(self, triplet, *args):
		"""Configure the build."""
		install_pfx	= self.install_pfx.joinpath(triplet)
		run("./configure",
			"--prefix=" + str(install_pfx),
			"--enable-shared" if (False != self.build_shared_libs) else "--disable-shared",
			"--enable-static" if (False == self.build_shared_libs) else "--disable-static",
			"--disable-mini-gmp",
			"--enable-x86-aesni",
			"--enable-x86-sha-ni",
			"--with-include-path=" + str(install_pfx.joinpath("include")),
			"--with-lib-path=" + str(install_pfx.joinpath("lib")),
			*args
		)

	def make(self):
		"""Runs the build."""
		run("make")

	def check(self):
		"""Checks the build."""
		run("make", "check")

	def install(self):
		"""Installs the build."""
		run("make", "install")

	def clean(self):
		"""Cleans the build."""
		run("git", "clean", "-fd")

class host_clg_pandeb9_t(host_t):
	def __del__(self):
		"""The destructor."""
		pass

	def __init__(self, user_args):
		"""The main constructor."""
		#---Call parent constructor---#
		super().__init__(user_args)

	def build_all(self):
		"""Builds all the supported targets."""
		configure_arg_arr	= [
			[
				"x86_64-linux",
				"--enable-pic",
				r"LDFLAGS=-Wl,-rpath=\$$ORIGIN/../lib",
			],
			[
				"i686-mingw",
				"--host=i686-w64-mingw32",
				"CC=i686-w64-mingw32-gcc",
			],
			[
				"x86_64-mingw",
				"--host=x86_64-w64-mingw32",
				"CC=x86_64-w64-mingw32-gcc",
			],
		]
		for configure_idx in range(0, len(configure_arg_arr)):
			configure_arg	= configure_arg_arr[configure_idx]
			self.configure(*configure_arg)
			self.make()
			if (0 == configure_idx):
				self.check()
			self.install()
			self.clean()

class host_github_linux_t(host_clg_pandeb9_t):
	def __del__(self):
		"""The destructor."""
		pass

	def __init__(self, user_args):
		"""The main constructor."""
		#---Call parent constructor---#
		super().__init__(user_args)






#---Define the hosts---#
host_names	= {
	"clg-pandeb9"	: host_clg_pandeb9_t,
	"github-linux"	: host_github_linux_t,
}

#---Parse the command line---#
parser	= argparse.ArgumentParser()
parser.add_argument("host"
	, type			= str
	, choices		= host_names.keys()
	, help			= "the name of the host this script is running on."
)
parser.add_argument("--install_pfx"
	, type			= pathlib.Path
	, default		= pathlib.Path(".").resolve().joinpath("install")
	, help			= "the installation path."
)
parser.add_argument("--build_shared_libs"
	, default		= False
	, action		= "store_true"
	, help			= "says whether to build shared libraries or static ones."
)
user_args	= parser.parse_args()

#---Create the host---#
host	= host_names[user_args.host](user_args)

#---Build all---#
os.chdir(str(pathlib.Path(__file__).parent.joinpath("nettle")))
host.build_all()
