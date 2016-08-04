#!/usr/bin/perl

# This perl script generates enzdes style constraints
# given a constraint specification file and a PDB ID
# Sample usage: perl generate_constraints.pl cst_spec.txt 1ABC.pdb

use Math::Trig;

$constraintSpecificationFile = $ARGV[0];
$lineCounter = 0;
open SPECFILE, "$constraintSpecificationFile" or die "Cannot open $constraintSpecificationFile for read!\n";
while($specLine = <SPECFILE>)
{
	$lineCounter ++;
}
close SPECFILE;
if($lineCounter%2 != 0)
{
	print "Error: Uneven number of constraint lines.\n";
	exit 0;
}
$numberOfConstraints = $lineCounter/2;
for($i = 1; $i <= $numberOfConstraints; $i ++)
{
	$CSTlineOne = $i + $i - 1;
	$CSTlineTwo = $i + $i;
	printConstraints($constraintSpecificationFile, $CSTlineOne, $CSTlineTwo);
}

sub printConstraints
{
	$CSTspecLineCounter = 0;
	open CSTSPECFILE, "$_[0]" or die "Cannot open $_[0] for read!\n";
	while($cstSpecLine = <CSTSPECFILE>)
	{
		chomp $cstSpecLine;
		$CSTspecLineCounter ++;
		if($CSTspecLineCounter == $_[1])
		{
			$cstSpecLineOne = $cstSpecLine;
		}
		if($CSTspecLineCounter == $_[2])
		{
			$cstSpecLineTwo = $cstSpecLine;
		}
	}
	close CSTSPECFILE;

	@cstSpecLineOneArray = split /\s+/, $cstSpecLineOne;
        @cstSpecLineTwoArray = split /\s+/, $cstSpecLineTwo;
        $chainOne = $cstSpecLineOneArray[0];
        $resOne = $cstSpecLineOneArray[1];
        $resOneAtomOne = $cstSpecLineOneArray[2];
        $resOneAtomTwo = $cstSpecLineOneArray[3];
        $resOneAtomThree = $cstSpecLineOneArray[4];
        $chainTwo = $cstSpecLineTwoArray[0];
        $resTwo = $cstSpecLineTwoArray[1];
        $resTwoAtomOne = $cstSpecLineTwoArray[2];
        $resTwoAtomTwo = $cstSpecLineTwoArray[3];
        $resTwoAtomThree = $cstSpecLineTwoArray[4];

	open PDBFILE, "$ARGV[1]" or die "Cannot open $ARGV[1] for read!\n";
        while($pdbLine = <PDBFILE>)
        {
                chomp $pdbLine;
                if($pdbLine =~ m/^ATOM/ || $pdbLine =~ m/^HETATM/)
                {
                        $atomTypeFull = substr($pdbLine, 12, 4);
                        @atomTypeArray = split /\s+/, $atomTypeFull;
                        $atomTypeArraySize = scalar @atomTypeArray;
                        if($atomTypeArraySize == 1)
                        {
                                $atomType = $atomTypeArray[0];
                        }
                        if($atomTypeArraySize > 1)
                        {
                                $atomType = $atomTypeArray[1];
                        }
                        $chain = substr($pdbLine, 21, 1);
                        $resNum = substr($pdbLine, 22, 4);
                        #print "$atomType $resOneAtomOne $chain $chainOne $resNum $resOne\n";
                        if($atomType eq $resOneAtomOne && $chain eq $chainOne && $resNum == $resOne)
                        {
				$resTypeOne = substr($pdbLine, 17, 4);
                                $pdbLineOne = $pdbLine;
                        }
                        #print "$atomType $resOneAtomTwo $chain $chainOne $resNum $resOne\n";
                        if($atomType eq $resOneAtomTwo && $chain eq $chainOne && $resNum == $resOne)
                        {
                                $pdbLineTwo = $pdbLine;
                        }
                        #print "$atomType $resOneAtomThree $chain $chainOne $resNum $resOne\n";
                        if($atomType eq $resOneAtomThree && $chain eq $chainOne && $resNum == $resOne)
                        {
                                $pdbLineThree = $pdbLine;
                        }
                        #print "$atomType $resTwoAtomOne $chain $chainTwo $resNum $resTwo\n";
                        if($atomType eq $resTwoAtomOne && $chain eq $chainTwo && $resNum == $resTwo)
                        {
				$resTypeTwo = substr($pdbLine, 17, 4);
                                $pdbLineFour = $pdbLine;
                        }
			#print "$atomType $resTwoAtomTwo $chain $chainTwo $resNum $resTwo\n";
                        if($atomType eq $resTwoAtomTwo && $chain eq $chainTwo && $resNum == $resTwo)
                        {
                                $pdbLineFive = $pdbLine;
                        }
			#print "$atomType $resTwoAtomThree $chain $chainTwo $resNum $resTwo\n";
                        if($atomType eq $resTwoAtomThree && $chain eq $chainTwo && $resNum == $resTwo)
                        {
                                $pdbLineSix = $pdbLine;
                        }
                }
        }
        close PDBFILE;

	#print "$pdbLineOne\n$pdbLineTwo\n$pdbLineThree\n$pdbLineFour\n$pdbLineFive\n$pdbLineSix\n";

	$distanceAB = getDistance($pdbLineOne, $pdbLineFour);
	$angle_A = get_angle($pdbLineTwo, $pdbLineOne, $pdbLineFour);
	$angle_B = get_angle($pdbLineOne, $pdbLineFour, $pdbLineFive);
	$torsion_A = getTorsionABCD($pdbLineThree, $pdbLineTwo, $pdbLineOne, $pdbLineFour);
	$torsion_AB = getTorsionABCD($pdbLineTwo, $pdbLineOne, $pdbLineFour, $pdbLineFive);
	$torsion_B = getTorsionABCD($pdbLineOne, $pdbLineFour, $pdbLineFive, $pdbLineSix);

	print "CST::BEGIN\n";

	print " TEMPLATE:: ATOM_MAP: 1 atom_name: $resOneAtomOne $resOneAtomTwo $resOneAtomThree\n";
	print " TEMPLATE:: ATOM_MAP: 1 residue3: $resTypeOne\n\n";

	print " TEMPLATE:: ATOM_MAP: 2 atom_name: $resTwoAtomOne $resTwoAtomTwo $resTwoAtomThree\n";
        print " TEMPLATE:: ATOM_MAP: 2 residue3: $resTypeTwo\n\n";

	print " CONSTRAINT:: distanceAB: $distanceAB 0.2 100 0 0\n";
	print " CONSTRAINT:: angle_A: $angle_A 10.0 10.0 360.0 1\n";
	print " CONSTRAINT:: angle_B: $angle_B 10.0 10.0 360.0 1\n";
	print " CONSTRAINT:: torsion_A: $torsion_A 20.0 10.0 360.0 1\n";
	print " CONSTRAINT:: torsion_AB: $torsion_AB 20.0 10.0 360.0 1\n";
	print " CONSTRAINT:: torsion_B: $torsion_B 20.0 10.0 360.0 1\n\n";

	print " ALGORITHM_INFO:: match_positions\n";
	print " ALGORITHM_INFO::END\n";
	print "CST::END\n";
}


sub getTorsionABCD
{
        $Ax = substr($_[0], 30, 8) + 0;
        $Ay = substr($_[0], 38, 8) + 0;
        $Az = substr($_[0], 46, 8) + 0;

        $Bx = substr($_[1], 30, 8) + 0;
        $By = substr($_[1], 38, 8) + 0;
        $Bz = substr($_[1], 46, 8) + 0;
        $Cx = substr($_[2], 30, 8) + 0;
        $Cy = substr($_[2], 38, 8) + 0;
        $Cz = substr($_[2], 46, 8) + 0;

        $Dx = substr($_[3], 30, 8) + 0;
        $Dy = substr($_[3], 38, 8) + 0;
        $Dz = substr($_[3], 46, 8) + 0;

        $BAx = $Bx - $Ax; $BAy = $By - $Ay; $BAz = $Bz - $Az;
        $BCx = $Bx - $Cx; $BCy = $By - $Cy; $BCz = $Bz - $Cz;
        $CBx = -1*$BCx; $CBy = -1*$BCy; $CBz = -1*$BCz;
        $CDx = $Cx - $Dx; $CDy = $Cy - $Dy; $CDz = $Cz - $Dz;

        $Px = $BAy*$BCz - $BAz*$BCy; $Py = $BAz*$BCx - $BAx*$BCz; $Pz = $BAx*$BCy - $BAy*$BCx;
        $Qx = $CBy*$CDz - $CBz*$CDy; $Qy = $CBz*$CDx - $CBx*$CDz; $Qz = $CBx*$CDy - $CBy*$CDx;

        $sign = ($BAx*$Qx + $BAy*$Qy + $BAz*$Qz) / ( sqrt($BAx*$BAx + $BAy*$BAy + $BAz*$BAz) * sqrt($Qx*$Qx + $Qy*$Qy + $Qz*$Qz) );
        if ($sign >= 0)
        {
                $sign = -1;
        }
        else
        {
                $sign = 1;
        }
        $torsion = $sign*(180/3.14159)*acos( ($Px*$Qx + $Py*$Qy + $Pz*$Qz) / ( sqrt($Px*$Px + $Py*$Py + $Pz*$Pz)*sqrt($Qx*$Qx + $Qy*$Qy + $Qz*$Qz)) );
 
	return sprintf("%4.2f", $torsion);
}

sub get_angle
{
	$angle = 0;

	$Ax = substr($_[0], 30, 8) + 0;
        $Ay = substr($_[0], 38, 8) + 0;
        $Az = substr($_[0], 46, 8) + 0;

        $Bx = substr($_[1], 30, 8) + 0;
        $By = substr($_[1], 38, 8) + 0;
        $Bz = substr($_[1], 46, 8) + 0;

	$Cx = substr($_[2], 30, 8) + 0;
        $Cy = substr($_[2], 38, 8) + 0;
        $Cz = substr($_[2], 46, 8) + 0;

	@BA = ($Ax - $Bx, $Ay - $By, $Az - $Bz);
	@BC = ($Cx - $Bx, $Cy - $By, $Cz - $Bz);

	$lengthBA = sqrt((($BA[0])**2)+(($BA[1])**2)+(($BA[2])**2));
	$lengthBC = sqrt((($BC[0])**2)+(($BC[1])**2)+(($BC[2])**2));

	@unitvectorBA = ($BA[0]/$lengthBA, $BA[1]/$lengthBA, $BA[2]/$lengthBA);
	@unitvectorBC = ($BC[0]/$lengthBC, $BC[1]/$lengthBC, $BC[2]/$lengthBC);

	$costheta = ($unitvectorBA[0]*$unitvectorBC[0])+($unitvectorBA[1]*$unitvectorBC[1])+($unitvectorBA[2]*$unitvectorBC[2]);
	$angle = acos($costheta) * 180.0 / pi;
	return sprintf("%4.3f", $angle);
}

sub getDistance
{
	$distance = 0;

	$Ax = substr($_[0], 30, 8) + 0;
	$Ay = substr($_[0], 38, 8) + 0;
	$Az = substr($_[0], 46, 8) + 0;

	$Bx = substr($_[1], 30, 8) + 0;
        $By = substr($_[1], 38, 8) + 0;
        $Bz = substr($_[1], 46, 8) + 0;

	$distance = sqrt(($Ax - $Bx)**2 + ($Ay - $By)**2 + ($Az - $Bz)**2);
	return sprintf("%4.2f", $distance); 
}
