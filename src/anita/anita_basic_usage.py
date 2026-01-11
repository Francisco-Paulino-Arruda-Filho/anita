from anita.anita_fo import check_proof

print(check_proof('''1. T A|B		pre
2. T A->C		pre
3. T B->C		pre
4. F C			conclusao
5. {	T A		1
6.	{	F A	    2
7.		@	    5,6
	}
8.	{	T C	    2
9.		@	    8,4
	}
   }
10.{	T B		1
11.	{	F B	    3
12.		@	    10,11
	}
13.	{	T C 	3
14.		@	    13,4
	}
   }
'''))

print(check_proof('''1. F A|~A conclusao
2. F A |F 1
3. F ~A 1
4. T A 3
5. @ 2,4
'''))

print(check_proof('''1. T A|B        pre
2. T A->C        pre
3. T B->C        pre
4. F C            conclusion
5. {    T A        1
6.    {    F A        2
7.        @        5,6
    }
8.    {    T C        2
9.        @        8,4
    }
   }
10.{    T B        1
11.    {    F B        3
12.        @        10,11
    }
13.    {    T C     3
14.        @        13,4
    }
   }
'''))