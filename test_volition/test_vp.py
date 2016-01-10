import volition.vp as vp

ifile = open("warble_fs1.vp", 'rb')
vp_file = vp.VolitionPackageFile(ifile)
ifile.close()
x = vp_file.get_file("data/music/title.wav")
print(x)

ofile = open("Title.wav", 'wb')
ofile.write(x.contents)
ofile.close()

vp_file.remove_file("data/music/title.wav")

ofile = open("test_warble.vp", 'wb')
test_vp_contents = vp_file.make_vp_file()
ofile.write(test_vp_contents)
ofile.close()
