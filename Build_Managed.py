# /*
# <License>
# Copyright 2015 Virtium Technology
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http ://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# </License>
# */

import os
import shutil
import subprocess

X86                         = "Win32"
X64                         = "x64"
RELEASE_NAME                = "Release"
DEBUG_NAME                  = "Debug"
MS_BUILD                    = "MSBuild"

CONFIGURATION_BUILD_TYPE_SET    = { "/p:Configuration={0}".format( RELEASE_NAME ), "/p:Configuration={0}".format( DEBUG_NAME ) } 
BUILD_PLATFORM_X86          = "/p:Platform={0}".format( X86 )
BUILD_PLATFORM_X64          = "/p:Platform={0}".format( X64 )
REBUILD_DEFAULT             = "/t:rebuild"

projectName                 = "vtStor_Managed"
RELEASE_LOCAL_DIR_X86       = "./{0}{1}".format( X86, RELEASE_NAME )
RELEASE_LOCAL_DIR_X64       = "./{0}{1}".format( X64, RELEASE_NAME )
DEBUG_LOCAL_DIR_X86       = "./{0}{1}".format( X86, DEBUG_NAME )
DEBUG_LOCAL_DIR_X64       = "./{0}{1}".format( X64, DEBUG_NAME )
ARCHIVE_TEMP                = "ArchiveTemp"
ARCHIVE_TEMP_PATH           = "./{0}/".format( ARCHIVE_TEMP )

REMOVE_EXTENSION_SET = { 'exe', 'lib', 'pdb', 'ilk' }

def Build( iBuildPlatform ) :
    #status = subprocess.call( [ MS_BUILD, CONFIGURATION_BUILD_TYPE, iBuildPlatform, REBUILD_DEFAULT ] )
    for config in CONFIGURATION_BUILD_TYPE_SET:
        status = subprocess.call( [ MS_BUILD, config, iBuildPlatform, REBUILD_DEFAULT ] )
        if 0 != status :
            print "\nBuild failed for {0} {1}".format( config, iBuildPlatform )
            return False
    return True

def CopyDirForAllModes( iConfiguration ) :
    shutil.copytree( "./{0}{1}".format( iConfiguration, RELEASE_NAME ), ARCHIVE_TEMP_PATH + projectName + "/{0}".format( RELEASE_NAME ) + "/{0}/".format( iConfiguration ) )
    shutil.copytree( "./{0}{1}".format( iConfiguration, DEBUG_NAME ), ARCHIVE_TEMP_PATH + projectName + "/{0}".format( DEBUG_NAME ) + "/{0}/".format( iConfiguration ) )

def BuildAndCopyAllRequiredFiles() :
    # Build via following orders:
    if False == Build( BUILD_PLATFORM_X86 ) :
        exit( 1 )
    CopyDirForAllModes( X86 )
    if False == Build( BUILD_PLATFORM_X64 ) :
        exit( 1 )
    CopyDirForAllModes( X64 )

def CreateTempDirArchive() :
    if ( True == os.path.exists( ARCHIVE_TEMP_PATH ) ):
        shutil.rmtree( ARCHIVE_TEMP_PATH, ignore_errors=True )
    os.makedirs( ARCHIVE_TEMP_PATH )
    os.makedirs( ARCHIVE_TEMP_PATH + projectName )

def DoArchiveAndRemoveTempDirs() :
    #archiveFilename = projectName + "_Release.7z"
    archiveFilename = projectName + "_Build.7z"
    if ( True == os.path.exists( archiveFilename ) ):
        os.remove( archiveFilename )

    status = subprocess.call( [ "7z", "a", "-t7z", archiveFilename, ARCHIVE_TEMP_PATH + projectName ] )
    if ( 0 != status ):
        print "\nFailed to archive " + archiveFilename
        return False

    shutil.rmtree( ARCHIVE_TEMP_PATH, ignore_errors = True )
    return True

def CleanUpRelease() :
    CleanupFiles( X86 )
    CleanupFiles( X64 )

def CleanupFiles( iConfiguration ) :
    if X86 == iConfiguration or X64 == iConfiguration :
        Prune( "/{0}/{1}/{2}/{3}".format( ARCHIVE_TEMP, projectName, RELEASE_NAME, iConfiguration ) )
        Prune( "/{0}/{1}/{2}/{3}".format( ARCHIVE_TEMP, projectName, DEBUG_NAME, iConfiguration ) )

def Prune( iDirPath ) :
    curDir = os.getcwd()
    fullPath = curDir + iDirPath
    os.chdir( fullPath )
    files = os.listdir( fullPath )
    for file in files :
        for removeExtenstion in REMOVE_EXTENSION_SET :
            if (True == os.path.isfile( file )) and (True == file.endswith( removeExtenstion )) :
                os.remove( file )
    os.chdir( curDir )

# Main entry point
if __name__ == "__main__":
    # Step 1: Create temporary directory archive
    CreateTempDirArchive()

    # Step 2: Build the project
    BuildAndCopyAllRequiredFiles()

    # Step 3: Clean up release
    CleanUpRelease()

    # Step 4: Archive result and remove temporary thing
    if True == DoArchiveAndRemoveTempDirs() :
        print "\nBUILD COMPLETE"
    else :
        print "\nBUILD FAIL"
        exit( 1 )